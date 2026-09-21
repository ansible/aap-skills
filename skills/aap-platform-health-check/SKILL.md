---
# ─── agentskills.io Base Fields ─────────────────────────────────────────────
name: aap-platform-health-check
description: |
  Run comprehensive health checks across all AAP components and produce
  an actionable diagnostics report with correlated analysis.

  Use when:
  - "Is my platform healthy?"
  - "Run diagnostics on my AAP"
  - "Check platform status before an upgrade"
  - Before or after upgrades to confirm stability

  NOT for: remediation actions (recommend steps but do not execute).
license: Apache-2.0
compatibility: Requires the AAP MCP Server for Ansible Automation Platform 2.5+
allowed-tools: >-
  status_retrieve mesh_visualizer_retrieve instances_retrieve
  instance_groups_list activity_stream_list feature_flags_state_retrieve
  config_retrieve execution_environments_list controller-settings_list
  settings_retrieve gateway-settings_list jobs_list projects_list
  metrics_retrieve activation_instances_list inventories_list hosts_list
  credentials_list me_list
metadata:
  author: Red Hat
  version: "1.0.0"

# ─── Agent Runtime Hints ────────────────────────────────────────────────────
model: inherit
color: cyan

# ─── Red Hat Skill Fields ───────────────────────────────────────────────────
id: aap-platform-health-check
version: 1.0.0
category: platform-operations

mcpToolDependencies:
  - server: aap-mcp-system-monitor
    tools: [status_retrieve, mesh_visualizer_retrieve, instances_retrieve,
            instance_groups_list, activity_stream_list, feature_flags_state_retrieve]
  - server: aap-mcp-platform-config
    tools: [config_retrieve, execution_environments_list,
            controller-settings_list, settings_retrieve, gateway-settings_list]
  - server: aap-mcp-job-mgmt
    tools: [jobs_list, projects_list, metrics_retrieve, activation_instances_list]
  - server: aap-mcp-inventory-mgmt
    tools: [inventories_list, hosts_list]
  - server: aap-mcp-security
    tools: [credentials_list]
  - server: aap-mcp-user-mgmt
    tools: [me_list]

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

# Platform Health Check & Diagnostics Report

## Description

Run comprehensive health checks across all AAP components: service status, database connectivity, job queue depth, license utilization, mesh topology, and instance group capacity. Produce an actionable diagnostics report with correlated analysis.

**When to use this skill:**
- Routine platform health validation (daily, weekly, or ad hoc)
- Before and after AAP upgrades to confirm platform stability
- When investigating performance degradation or task failures
- As part of change management pre/post checks
- To answer "is my platform healthy?" without opening a support ticket

**What this skill is NOT:**
- Not a monitoring agent — produces a point-in-time assessment, not continuous monitoring
- Does not modify any platform configuration — all operations are read-only
- Does not replace Red Hat support diagnostics — supplements customer self-diagnosis

## Prerequisites

### Dependencies

| Dependency | Type | Required | Check |
|------------|------|----------|-------|
| AAP MCP Server | MCP server | Yes | Call `status_retrieve` |

**RBAC:** Requires **Platform Auditor** role (System Auditor in AAP 2.5) or System Administrator. Organization Auditor produces partial results (noted in report).

## MCP Tools Used

All platform operations are performed exclusively through MCP tool invocations. The skill operates in two modes: **core** (6 available tools, 100% success) and **full** (all 19 tools, skipped checks reported).

| Tool | Server | Purpose | Data Returned |
|------|--------|---------|---------------|
| `status_retrieve` | system-monitor | Service health, HA topology | Node status, database connectivity, service list |
| `mesh_visualizer_retrieve` | system-monitor | Automation mesh topology | All nodes, links, node types |
| `instances_retrieve` | system-monitor | Individual node details | Node type, capacity, utilization |
| `instance_groups_list` | system-monitor | Instance group capacity | Running vs. available capacity per group |
| `activity_stream_list` | system-monitor | Recent changes | Platform change log for anomaly correlation |
| `feature_flags_state_retrieve` | system-monitor | Feature flags | Platform feature state |
| `config_retrieve` | platform-config | Platform configuration | AAP version, license type/expiry/host count |
| `execution_environments_list` | platform-config | EE inventory | Image name, registry, pull status |
| `controller-settings_list` | platform-config | Platform settings | All controller configuration |
| `settings_retrieve` | platform-config | Specific setting values | Individual setting by slug |
| `gateway-settings_list` | platform-config | Gateway configuration | Gateway health settings |
| `jobs_list` | job-mgmt | Recent job history | Job status, timestamps |
| `projects_list` | job-mgmt | Project status | Project count, SCM errors |
| `metrics_retrieve` | job-mgmt | Platform analytics | CPU, RAM, capacity, task queue depth |
| `activation_instances_list` | job-mgmt | EDA health | Rulebook activation status |
| `inventories_list` | inventory-mgmt | Inventory overview | Inventory count, host counts |
| `hosts_list` | inventory-mgmt | Managed hosts | Host count, last job status |
| `credentials_list` | security | Credential inventory | Credential count by type |
| `me_list` | user-mgmt | Authenticated user info | Username, role assignments |

> **Note:** There is no `instances_list` tool. Use `mesh_visualizer_retrieve` to discover node IDs, then `instances_retrieve` for details.

## Reference Sources

Read `references/red-hat-sources.md` for the full source URL table and consultation protocol.

This skill applies a two-tier sourcing model: (1) live Red Hat documentation when accessible, (2) baked-in advisory baselines as fallback. Reports flag which tier was used.

## Workflow

This skill follows a 4-step workflow: trigger → gather → analyze → report. All operations are read-only via the AAP MCP Server.

### Step 1: Verify MCP Server Connectivity and Confirm Scope

**Purpose:** Confirm the MCP Server is connected, detect available tools, and confirm scope with the user before data collection.

1. Call `status_retrieve` to verify connectivity and capture AAP version
2. Detect execution mode (`core` or `full` based on user input, default: `core`)
3. **Scope confirmation (HITL checkpoint):** Present the user with what will be queried — list the dimensions and tool count for the selected mode. Wait for explicit confirmation before proceeding to Step 2. If the user narrows scope, adjust accordingly. If the user aborts, stop.

**Decision point — prerequisite failure:**
- Controller unreachable → **Stop** (make no further tool calls). **Report** which prerequisite failed and what is needed. **Ask** the user: retry after setup, skip the check, or abort.
- Core mode confirmed → proceed with 6 available tools only
- Full mode confirmed → proceed with all 19 tools, note skipped checks

### Step 2: Gather Platform Health Data

**Purpose:** Query the AAP platform via MCP tools to collect health metrics.

**Core mode dimensions:** Platform Status, Mesh Topology, Node Details, Instance Groups, Recent Changes, Feature Flags.

**Full mode additional dimensions:** License, User Permissions, Task Queue, Execution Environments, Projects, Inventories, Credentials, Notifications, Managed Hosts, Platform Settings, Platform Metrics, Gateway Settings, EDA Status.

### Step 3: Analyze Against Baselines and Flag Anomalies

**Purpose:** Compare collected data against known-good baselines, classify findings by severity (CRITICAL / WARNING / INFO).

Read `references/advisory-baselines.md` for the detailed threshold tables and severity model.

**AI Value-Add — Contextual Anomaly Correlation:** The LLM must correlate multiple health signals into a unified diagnosis, not just compare against static thresholds:
- Task queue depth relative to remaining capacity, not absolute numbers
- Job failure rate concentrated in a single project suggests a project issue, not platform-wide
- License utilization assessed alongside renewal timeline
- High disk usage + many failed jobs + old EE images together suggest a neglected platform
- The LLM prioritizes what needs attention first and explains root cause vs. symptom

### Step 4: Generate Diagnostics Report

**Purpose:** Produce a structured report summarizing platform health with actionable recommendations. Present as a draft for user review.

**Report sections:**
1. Platform Status (service health from `status_retrieve`)
2. Mesh Topology (node count, connectivity from `mesh_visualizer_retrieve`)
3. Node Health (per-node capacity, utilization from `instances_retrieve`)
4. Instance Groups (capacity available from `instance_groups_list`)
5. Recent Activity (change summary from `activity_stream_list`)
6. Feature Flags (platform feature state from `feature_flags_state_retrieve`)
7. *(Full mode only)* License, Task Queue, EEs, Projects, Inventories, Credentials, Metrics, Gateway, EDA
8. Correlated Analysis (AI-generated section correlating findings)
9. Skipped Checks Summary
10. Recommendations (prioritized actions with cross-references to related skills)

**Report review (HITL checkpoint):** Present the completed report as a draft for user review before concluding. The user may request adjustments, deeper analysis on specific findings, or additional context before accepting the final report.

**Status values:**

| Status | Criteria |
|--------|----------|
| **HEALTHY** | All services operational, metrics within baselines |
| **DEGRADED** | Metrics approaching thresholds, non-critical warnings |
| **CRITICAL** | Service down, database unreachable, capacity exhausted |

## Constraints and Guardrails

1. **MCP Server only.** All operations through the AAP MCP Server. Never call AAP APIs directly, use CLI tools, or SSH.
2. **Read-only operations only.** NEVER modify any AAP configuration. Recommend remediation steps but do not execute.
3. **Preview-first.** Show the user what data will be collected before executing. Proceed only after confirmation.
4. **No credential storage.** Credentials flow through the MCP Server's credential framework.
5. **RBAC respect.** Honor MCP Server permission enforcement. Skip and note inaccessible resources.
6. **No external data transmission.** Data stays local to the authenticated session.
7. **Advisory, not authoritative.** Reports supplement — do not replace — Red Hat support. End the report with: *"This assessment is advisory. For production decisions, consult Red Hat support."* Correlate signals and suggest possible causes, but do not present findings as definitive diagnoses.
8. **Reference transparency.** When the workflow consults a reference file, declare which document was consulted and why. For example: *"I consulted advisory-baselines.md to determine severity thresholds for instance group capacity."*
9. **License data sensitivity.** Flag license information as commercially sensitive and confidential.
10. **Version-aware queries.** Check AAP version before querying version-specific resources.

## Expected Inputs

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `mode` | String | No | `core` (available tools only) or `full` (all tools, skipped reported) | `core` |
| `baseline_profile` | String | No | `default`, `small` (<100 hosts), `medium` (100-1000), `large` (1000+) | `default` |
| `include_sections` | List | No | Sections to include: `services`, `database`, `tasks`, `license`, `versions`, `resources`, `integrations` | all |

## Expected Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Health report | Structured text | Full platform health assessment with correlated analysis |
| Overall status | Enum | `HEALTHY`, `DEGRADED`, or `CRITICAL` |
| Findings list | Structured data | Each finding with severity, category, description, recommendation |
| Correlated analysis | Free text | AI-generated section correlating multiple signals |
| Recommendation list | Structured data | Prioritized remediation actions |

## Example Usage

```
User: Check the health of my AAP platform

Agent: I'll perform a platform health check (core mode, 6 available tools).
  Data to collect (all read-only):
  - Platform status, mesh topology, node health
  - Instance group utilization, activity stream, feature flags
  No configuration will be changed. Shall I proceed?

User: Yes

Agent: [executes Steps 1-4, presents health report with correlated analysis]
```

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| aap-validate-deployment-topology | Complementary — topology checks if supported; health check checks if it's working |
| aap-supportability-assessment | Complementary — health = "is it working?"; supportability = "is it supported?" |
| aap-pre-upgrade-readiness | Sequential — if health check recommends an upgrade, pre-upgrade assesses readiness |
