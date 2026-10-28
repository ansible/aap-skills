---
# ─── agentskills.io Base Fields ─────────────────────────────────────────────
name: aap-supportability-assessment
description: |
  Scan the entire AAP platform configuration and classify every component
  as Supported, Partially Supported, or Unsupported against Red Hat's
  published support matrix.

  Use when:
  - "Is this configuration supported by Red Hat?"
  - "Check supportability before opening a support case"
  - "Audit my AAP for unsupported components"
  - During quarterly operational reviews to catch configuration drift

  NOT for: platform health checks (use aap-platform-health-check instead).
license: Apache-2.0
compatibility: Requires the AAP MCP Server for Ansible Automation Platform 2.5+
allowed-tools: >-
  status_retrieve config_retrieve me_list instance_groups_list
  execution_environments_list projects_list notification_templates_list
  mesh_visualizer_retrieve credentials_list credential_types_list
  instances_retrieve inventories_list hosts_list job_templates_list
  workflow_job_templates_list controller-settings_list settings_retrieve
  metrics_retrieve feature_flags_state_retrieve authenticators_list
  organizations_list users_list teams_list activity_stream_list
  gateway-settings_list jobs_list
metadata:
  author: Red Hat
  version: "0.1.0"

# ─── Agent Runtime Hints ────────────────────────────────────────────────────
model: inherit
color: cyan

# ─── Red Hat Skill Fields ───────────────────────────────────────────────────
id: aap-supportability-assessment
version: 0.1.0
category: platform-operations

# The AAP MCP Server is a single MCP server, named "aap". It exposes all tools at
# /mcp and subsets at /mcp/<toolset>; the server name is "aap" on every endpoint.
# Toolset membership is recorded in comments below — it determines which endpoint
# serves a tool, but it is not part of the server's identity.
mcpToolDependencies:
  - server: aap
    tools:
      # system_monitoring
      - status_retrieve
      - mesh_visualizer_retrieve
      - instances_retrieve
      - instance_groups_list
      - activity_stream_list
      - feature_flags_state_retrieve
      # platform_configuration
      - config_retrieve
      - execution_environments_list
      - notification_templates_list
      - controller-settings_list
      - settings_retrieve
      - gateway-settings_list
      # job_management
      - jobs_list
      - projects_list
      - metrics_retrieve
      - job_templates_list
      - workflow_job_templates_list
      # inventory_management
      - inventories_list
      - hosts_list
      # security_compliance
      - credentials_list
      - credential_types_list
      # user_management
      - me_list
      - authenticators_list
      - organizations_list
      - users_list
      - teams_list

supportBoundary:
  model: red-hat
  dependencies:
    - name: aap-mcp-server
      supportStatus: tech-preview

# ─── AAP Operational Profile ────────────────────────────────────────────────
riskLevel: read-only
sensitiveData: false
aapVersion: ">=2.5"

---

# Assess Platform Supportability State

Follow [`context/output-format.md`](../../context/output-format.md) for report structure, Markdown formatting, save options, and the standard MCP quick reference and footer.

## Description

Scan the entire AAP platform configuration and classify every component: **Supported / Partially Supported / Unsupported**. Flag community collections vs. certified, custom EEs with unknown base images, custom credential types, deprecated settings, and unsupported authentication backends.

**When to use this skill:**
- Before opening a Red Hat support case — confirm the environment is in a supported state
- Before and after AAP upgrades — validate the new configuration is supported
- During quarterly operational reviews — catch configuration drift into unsupported states
- When adding new collections, EEs, or integrations — verify compatibility

**What this skill is NOT:**
- Not a substitute for Red Hat support — provides a self-service pre-check
- Does not modify any platform configuration — all operations are read-only
- Does not validate application-level automation content (playbooks, roles)
- Does not access Red Hat's internal support systems

## Prerequisites

### Dependencies

| Dependency | Type | Required | Check |
|------------|------|----------|-------|
| AAP MCP Server | MCP server | Yes | Call `status_retrieve` |

**RBAC:** Requires **Platform Auditor** role (System Auditor in AAP 2.5) or System Administrator. Organization Auditor is NOT sufficient — partial visibility produces misleading results.

## MCP Tools Used

| Tool | Server | Purpose | Data Returned |
|------|--------|---------|---------------|
| `status_retrieve` | system-monitor | Service health | Component status |
| `config_retrieve` | platform-config | Platform config | AAP version, license, IS_K8S flag |
| `me_list` | user-mgmt | Authenticated user | Role assignments |
| `instance_groups_list` | system-monitor | Instance groups | Group types, capacity |
| `execution_environments_list` | platform-config | EE inventory | Image, registry, managed flag |
| `projects_list` | job-mgmt | Projects | Project count, SCM type |
| `notification_templates_list` | platform-config | Notifications | Template types |
| `mesh_visualizer_retrieve` | system-monitor | Topology | Node types, mesh links |
| `credentials_list` | security | Credentials | Count by type |
| `credential_types_list` | security | Credential type defs | Standard vs. custom vs. external |
| `instances_retrieve` | system-monitor | Node details | Node type, capacity |
| `inventories_list` | inventory-mgmt | Inventories | Count, smart inventory status |
| `hosts_list` | inventory-mgmt | Managed hosts | Host count |
| `job_templates_list` | job-mgmt | Job templates | Template count |
| `workflow_job_templates_list` | job-mgmt | Workflow templates | Workflow count |
| `controller-settings_list` | platform-config | Controller settings | Deprecated value detection |
| `settings_retrieve` | platform-config | Specific settings | Non-default settings via slug `changed` |
| `metrics_retrieve` | job-mgmt | Platform metrics | DB connections, capacity |
| `feature_flags_state_retrieve` | system-monitor | Feature flags | Flags affecting supportability |
| `authenticators_list` | user-mgmt | Auth backends | Authentication providers |
| `organizations_list` | user-mgmt | Organizations | Org count |
| `users_list` | user-mgmt | Users | User count, superuser status |
| `teams_list` | user-mgmt | Teams | Team count |
| `activity_stream_list` | system-monitor | Recent changes | Platform change log for configuration drift detection |
| `gateway-settings_list` | platform-config | Gateway configuration | Gateway health settings |
| `jobs_list` | job-mgmt | Recent jobs | Job patterns, failure trends |

> **Known gaps:** Collections (Hub API), Database engine/version, Python version are NOT available via MCP.

## Reference Sources

Read `references/red-hat-sources.md` for the full source URL table and source consultation protocol.

This skill uses a two-tier sourcing model: (1) live Red Hat documentation (prioritizing the Product Life Cycle Data API for deterministic version classification), (2) baked-in rules as fallback.

## Workflow

This skill follows a 4-step workflow: trigger → inventory → cross-reference → report. All operations are read-only via the AAP MCP Server.

### Step 1: Verify MCP Server Connectivity and Permissions

**Purpose:** Confirm connectivity and platform-wide visibility.

1. `status_retrieve` — verify connectivity, capture component status
2. `config_retrieve` — capture AAP version, license type
3. `me_list` — retrieve role assignments
4. Validate Platform Auditor or System Administrator permissions

**Decision point — prerequisite failure:**
- Controller unreachable → **Stop** (make no further tool calls). **Report** which prerequisite failed and what is needed. **Ask** the user: retry after setup, skip the check, or abort.
- Only Organization Auditor or lower → **Stop** (partial assessment would be misleading).

5. **Scope confirmation (HITL checkpoint):** Present the user with what will be assessed — list the supportability dimensions and MCP tools to be queried. Wait for explicit confirmation before proceeding to Step 2. If the user narrows scope, adjust accordingly. If the user aborts, stop.

### Step 2: Inventory Current Platform State

**Purpose:** Collect a complete picture of the platform's configuration across all supportability dimensions.

**Dimensions inventoried:** AAP Version, Deployment Topology, Instance Groups, Execution Environments, Credential Types, Credentials, Authentication, Notifications, SCM Configuration, Platform Settings, Feature Flags, Platform Metrics.

**Extended dimensions (require CaC setup):** Installed Collections, Database engine/version, Python Runtime. When unavailable, noted as "NOT ASSESSED" in report.

### Step 3: Cross-Reference Against Support Matrix

**Purpose:** Compare each dimension against Red Hat's published supported configurations.

Read `references/support-matrix-rules.md` for the detailed assessment rules covering all 8 categories:
1. **AAP Version** — lifecycle phase via Product Life Cycle Data API
2. **Deployment Topology** — match against 6 tested deployment models
3. **Database** — PostgreSQL version requirements (manual check required)
4. **Collections** — certified vs. validated vs. community classification
5. **Execution Environments** — managed vs. custom, EE lifecycle policy
6. **Authentication** — supported backends under Gateway pluggable auth
7. **External Credential Lookups** — supported plugin list
8. **Deprecated Features** — deprecated/removed items per AAP version

**Supportability classification:**

| Classification | Meaning |
|---------------|---------|
| **PASS** | Matches published support matrix |
| **WARN** | Supported with caveats (approaching EOL, deprecated but covered) |
| **FAIL** | Does not match any supported configuration |
| **INFO** | Cannot determine (custom components, no matrix entry) |

**AI Value-Add — Contextual Classification:** Cross-reference findings for compound risks, prioritize by impact, explain support boundaries for custom components, recommend timelines for approaching EOL.

### Step 4: Generate Supportability Report

**Purpose:** Produce a structured report with per-dimension classification and remediation guidance.

**Report sections:**
1. Overall supportability status
2. Platform version (lifecycle phase, support dates)
3. Deployment topology
4. Database (manual check required if CaC unavailable)
5. Python runtime (manual check required if CaC unavailable)
6. Collections (manual check required if CaC unavailable)
7. Execution environments
8. Authentication backends
9. External credential lookups
10. Platform settings (deprecated, non-default)

**Report review (HITL checkpoint):** Present the completed report as a draft for user review before concluding. The user may request adjustments, deeper analysis on specific dimensions, or additional context before accepting the final report.

**Status values:**

| Status | Criteria |
|--------|----------|
| **FULLY SUPPORTED** | All assessed dimensions PASS |
| **PARTIALLY SUPPORTED** | One or more WARN but no FAIL |
| **UNSUPPORTED CONFIGURATION DETECTED** | One or more FAIL findings |

## Constraints and Guardrails

1. **MCP Server only.** All operations through the AAP MCP Server. Never call AAP APIs directly, use CLI tools, or SSH.
2. **Read-only operations only.** NEVER modify any AAP configuration.
3. **Preview-first.** Show the user what data will be collected before executing.
4. **No credential storage.** Credentials flow through the MCP Server's credential framework.
5. **RBAC respect.** Require Platform Auditor for full assessment. Do not attempt partial assessment with lower permissions.
6. **No external data transmission.** Platform configuration data stays local.
7. **Publicly available references only.** Cite only publicly available Red Hat documentation.
8. **Advisory, not authoritative.** Include disclaimer: not an official Red Hat supportability determination. End the report with: *"This assessment is advisory. For production decisions, consult Red Hat support."*
9. **Reference transparency.** When the workflow consults a reference file, declare which document was consulted and why. For example: *"I consulted support-matrix-rules.md to classify execution environments against the Red Hat support matrix."*
10. **No false assurance.** If status cannot be determined, classify as INFO/Unknown rather than assuming supported.
11. **Version-aware queries.** Check AAP version before querying version-specific resources.
12. **Confidentiality.** Flag reports containing topology, credentials, or integration details as confidential.

## Expected Inputs

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `include_sections` | List | No | Dimensions to assess | all |
| `strict_mode` | Boolean | No | If `true`, flag validated-but-not-certified collections as warnings | `false` |
| `target_version` | String | No | Also check compatibility with a target AAP version | — |

## Expected Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Supportability report | Structured text | Full assessment with per-dimension classification |
| Overall status | Enum | `FULLY_SUPPORTED`, `PARTIALLY_SUPPORTED`, or `UNSUPPORTED_CONFIGURATION_DETECTED` |
| Findings list | Structured data | Each finding with classification, dimension, remediation |
| Remediation plan | Structured data | Prioritized actions to achieve fully supported state |

## Example Usage

```
User: Check if my AAP deployment is fully supported.

Agent: I'll perform a supportability assessment. Data to collect (all read-only):
  - Platform version, topology, EEs, credentials, authentication, settings
  No configuration will be changed. Results are advisory. Shall I proceed?

User: Yes.

Agent: [executes Steps 1-4, presents supportability report with per-dimension classification]
```

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| aap-validate-deployment-topology | Overlapping — topology skill goes deeper on topology; this skill covers topology as one of 10 dimensions |
| aap-platform-health-check | Complementary — health = "is it working?"; supportability = "is it supported?" |
| aap-pre-upgrade-readiness | Sequential — if this skill recommends upgrading, pre-upgrade assesses readiness |
