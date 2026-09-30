---
# ─── agentskills.io Base Fields ─────────────────────────────────────────────
name: aap-pre-upgrade-readiness
description: |
  Assess AAP platform readiness for upgrade to a target version. Checks
  upgrade path validity, deprecated features, EE compatibility, authentication
  backends, and topology support.

  Use when:
  - "Can I upgrade to AAP 2.6?"
  - "Check upgrade readiness for my platform"
  - "What will break if I upgrade?"
  - Planning an AAP version upgrade and need a pre-assessment

  NOT for: executing upgrades (use the official Red Hat upgrade guide instead).
license: Apache-2.0
compatibility: Requires the AAP MCP Server for Ansible Automation Platform 2.5+
allowed-tools: >-
  status_retrieve config_retrieve me_list instance_groups_list
  execution_environments_list projects_list notification_templates_list
  mesh_visualizer_retrieve credentials_list credential_types_list
  instances_retrieve inventories_list hosts_list job_templates_list
  workflow_job_templates_list controller-settings_list settings_retrieve
  metrics_retrieve feature_flags_state_retrieve authenticators_list
  jobs_list
metadata:
  author: Red Hat
  version: "0.1.0"

# ─── Agent Runtime Hints ────────────────────────────────────────────────────
model: inherit
color: cyan

# ─── Red Hat Skill Fields ───────────────────────────────────────────────────
id: aap-pre-upgrade-readiness
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
      - feature_flags_state_retrieve
      # platform_configuration
      - config_retrieve
      - execution_environments_list
      - notification_templates_list
      - controller-settings_list
      - settings_retrieve
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

# Pre-Upgrade Readiness Check

## Description

Assess platform readiness for upgrade to a target AAP version. Performs a comprehensive pre-upgrade analysis across every dimension that can cause an upgrade to fail or produce unexpected results: upgrade path validity, deprecated settings, EE compatibility, credential types, authentication backends, topology compatibility, and custom content risk.

**When to use this skill:**
- Before planning an AAP upgrade — identify blockers and required pre-work
- As part of change management — provide evidence of readiness assessment for CAB approval
- When evaluating upgrade urgency — understand the gap between current and target versions
- After supportability assessment recommends an upgrade — assess what the upgrade entails

**What this skill is NOT:**
- Not an upgrade executor — does not modify any platform configuration
- Does not replace Red Hat's official upgrade guide — supplements with platform-specific pre-assessment
- Does not validate the upgrade itself — validates readiness before the upgrade begins

## Prerequisites

### Dependencies

| Dependency | Type | Required | Check |
|------------|------|----------|-------|
| AAP MCP Server | MCP server | Yes | Call `status_retrieve` |

**RBAC:** Requires **Platform Auditor** role (System Auditor in AAP 2.5) or System Administrator. Organization Auditor is NOT sufficient — partial visibility produces incomplete readiness results.

## MCP Tools Used

| Tool | Server | Purpose | Data Returned |
|------|--------|---------|---------------|
| `status_retrieve` | system-monitor | Service health | Component status |
| `config_retrieve` | platform-config | Platform config | AAP version, license, IS_K8S |
| `me_list` | user-mgmt | User permissions | Role assignments |
| `instance_groups_list` | system-monitor | Instance groups | Group config, capacity |
| `execution_environments_list` | platform-config | EE inventory | Image, registry, managed flag |
| `projects_list` | job-mgmt | Projects | SCM types, project count |
| `notification_templates_list` | platform-config | Notifications | Integration types |
| `mesh_visualizer_retrieve` | system-monitor | Topology | Nodes, links, types |
| `credentials_list` | security | Credentials | Count by type |
| `credential_types_list` | security | Credential type defs | Standard vs. custom |
| `instances_retrieve` | system-monitor | Node details | Node type, capacity |
| `inventories_list` | inventory-mgmt | Inventories | Count, types |
| `hosts_list` | inventory-mgmt | Hosts | Host count |
| `job_templates_list` | job-mgmt | Job templates | Template config |
| `workflow_job_templates_list` | job-mgmt | Workflow templates | Workflow config |
| `controller-settings_list` | platform-config | Controller settings | Deprecated setting detection |
| `settings_retrieve` | platform-config | Specific settings | Individual setting by slug |
| `metrics_retrieve` | job-mgmt | Platform metrics | Capacity, jobs, DB connections |
| `feature_flags_state_retrieve` | system-monitor | Feature flags | Version-sensitive flags |
| `authenticators_list` | user-mgmt | Auth backends | Authentication providers |
| `jobs_list` | job-mgmt | Recent jobs | Running/pending for operational readiness |

> **Known gaps:** Database engine/version, collection compatibility, EE internal versions (Python, ansible-core) are NOT available via MCP — flagged for manual verification.

## Reference Sources

Read `references/red-hat-sources.md` for the full source URL table and consultation protocol.

Read `references/upgrade-matrices.md` for the detailed version-specific upgrade paths, deprecated features, EE compatibility, authentication migration, and topology changes.

## Workflow

This skill follows a 4-step workflow: trigger → gather → assess → report. All operations are read-only via the AAP MCP Server.

### Step 1: Verify Permissions and Detect Current Version

**Purpose:** Confirm platform-wide visibility and establish the upgrade path.

1. `status_retrieve` — verify connectivity, capture component health
2. `config_retrieve` — capture current AAP version, license, IS_K8S
3. `me_list` — retrieve role assignments
4. Validate Platform Auditor or System Administrator permissions
5. Store current version for upgrade path calculation

**Decision point — prerequisite failure:**
- Controller unreachable → **Stop** (make no further tool calls). **Report** which prerequisite failed and what is needed. **Ask** the user: retry after setup, skip the check, or abort.
- Organization Auditor or lower → **Stop**. Partial visibility produces incomplete readiness results.

6. **Scope confirmation (HITL checkpoint):** Present the user with what will be assessed — list the upgrade dimensions, target version, and MCP tools to be queried. Wait for explicit confirmation before proceeding to Step 2. If the user narrows scope, adjust accordingly. If the user aborts, stop.

### Step 2: Gather Current Platform State

**Purpose:** Collect a comprehensive inventory of everything that could be affected by an upgrade.

**Dimensions gathered:** Platform Version, Platform Settings, Execution Environments, Credential Types, Authentication Backends, Topology, Jobs (running/pending), Projects, Inventories, Job Templates, Workflow Templates, Credentials, Notifications, Feature Flags.

**Custom content detection (critical for upgrade risk):** Flag custom credential types (`managed_by_tower: false`), custom EEs (non-managed), non-standard auth backends, webhook notifications.

### Step 3: Assess Upgrade Readiness

**Purpose:** Evaluate platform state against target version requirements. Each dimension receives PASS / WARN / FAIL.

Read `references/upgrade-matrices.md` for the detailed assessment matrices covering:
- **3.1 Upgrade Path Validity** — supported paths by deployment type and RHEL version
- **3.2 Database Compatibility** — PostgreSQL requirements (manual check required)
- **3.3 Deprecated Settings** — features deprecated or removed in target version
- **3.4 Collection Compatibility** — migration requirements (manual check required)
- **3.5 EE Compatibility** — base image and ansible-core version requirements
- **3.6 Authentication Compatibility** — 2.4→2.6 vs 2.5→2.6 migration differences
- **3.7 Topology Compatibility** — infrastructure changes by source version
- **3.8 Custom Content Risk** — risk assessment based on custom content count
- **3.9 Operational Readiness** — running jobs, active schedules, backup status

**AI Value-Add — Contextual Risk Assessment:** The LLM must correlate findings across dimensions. 50 custom EEs = much higher upgrade risk. Extensive custom content + RHEL 8 source = compounded scope. Multiple custom auth backends + custom credentials + custom EEs = cross-cutting risk. Quantify: "50 EEs require rebuild — estimate 2-4 hours." Prioritize what blocks, what increases risk, what requires the most lead time.

### Step 4: Generate Readiness Report

**Purpose:** Produce a structured report with overall readiness, per-dimension assessment, and pre-upgrade checklist.

**Report sections:**
1. Upgrade path summary (current → target, path type)
2. Pre-flight checks (PASS/FAIL/MANUAL CHECK table for each dimension)
3. Component compatibility (EEs, credential types, notifications)
4. Breaking changes (deprecated settings, auth migration, API changes)
5. Custom content risk summary
6. Estimated complexity and recommended maintenance window
7. Rollback plan considerations

**Report review (HITL checkpoint):** Present the completed report as a draft for user review before concluding. The user may request adjustments, deeper analysis on specific dimensions, or additional context before accepting the final report.

**Status values:**

| Status | Criteria |
|--------|----------|
| **READY** | All checks PASS; no blockers |
| **BLOCKED** | One or more FAIL findings that must be resolved first |
| **NEEDS REMEDIATION** | WARN or MANUAL CHECK items; upgrade possible after remediation |

## Constraints and Guardrails

1. **MCP Server only.** All operations through the AAP MCP Server. Never call AAP APIs directly, use CLI tools, or SSH.
2. **Read-only operations only.** NEVER modify any AAP configuration. This skill assesses readiness — it does not execute upgrade steps.
3. **Preview-first.** Show the user what data will be collected before executing.
4. **No credential storage.** Credentials flow through the MCP Server's credential framework.
5. **RBAC respect.** Require Platform Auditor for full assessment. Do not attempt partial assessment.
6. **No external data transmission.** Platform configuration data stays local.
7. **Publicly available references only.** Cite only publicly available Red Hat documentation.
8. **Advisory only.** Include disclaimer: this is a readiness pre-assessment, not an upgrade procedure. End the report with: *"This assessment is advisory. For production decisions, consult Red Hat support and the official upgrade guide."*
9. **Reference transparency.** When the workflow consults a reference file, declare which document was consulted and why. For example: *"I consulted upgrade-matrices.md to determine the supported upgrade path from 2.5 to 2.6."*
10. **No false assurance.** If compatibility cannot be determined, classify as INFO/Unknown and recommend staging tests.
11. **Version-aware queries.** Check AAP version before querying version-specific resources.
12. **Confidentiality.** Flag reports with topology, credentials, and custom content details as confidential.

## Expected Inputs

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `target_version` | String | **Yes** | Target AAP version (e.g., `"2.6"`, `"2.7"`) | — |
| `include_sections` | List | No | Dimensions to assess | all |

## Expected Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Readiness report | Structured text | Full upgrade readiness assessment |
| Overall status | Enum | `READY`, `BLOCKED`, or `NEEDS_REMEDIATION` |
| Pre-upgrade checklist | Structured data | Prioritized actions: BLOCKER, MANUAL CHECK, RECOMMENDED |
| Risk summary | Structured data | Compound risks, complexity, time estimates |
| Impact scope | Structured data | Counts of all resources affected |

## Example Usage

```
User: I want to upgrade my AAP platform to version 2.6. Can you check if we're ready?

Agent: I'll perform a pre-upgrade readiness assessment. Data to collect (all read-only):
  - Platform version, settings, EEs, credentials, authentication, topology
  - Running jobs and operational state
  Database and collection compatibility require manual verification.
  No configuration will be changed. Results are advisory. Shall I proceed?

User: Yes

Agent: [executes Steps 1-4, presents readiness report]

  Status: NEEDS REMEDIATION
  Upgrade path: 2.5 → 2.6 (DIRECT, supported)

  Blockers: None
  Manual checks required:
  - Database: Verify PostgreSQL 15+ (not available via MCP)
  - Collections: Verify ansible.platform migration (not available via MCP)

  Warnings:
  - 3 custom EEs detected — rebuild and test against ansible-core 2.16+
  - RPM deployment — plan containerized migration before 2.7
  - ServiceNow notification template — deprecated for Zurich+

  Estimated complexity: MEDIUM (3 custom EEs, 2 manual checks)
```

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| aap-validate-deployment-topology | Complementary — topology validates current architecture; this skill checks target version compatibility |
| aap-platform-health-check | Sequential — resolve health issues before assessing upgrade readiness |
| aap-supportability-assessment | Sequential — supportability says "you should upgrade"; this skill says "here's what you need to do first" |
