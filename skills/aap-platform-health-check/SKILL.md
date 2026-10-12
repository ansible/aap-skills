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
  version: "1.1.0"

# ─── Agent Runtime Hints ────────────────────────────────────────────────────
model: inherit
color: cyan

# ─── Red Hat Skill Fields ───────────────────────────────────────────────────
id: aap-platform-health-check
version: 1.1.0
category: platform-operations

# The AAP MCP Server is a single MCP server, named "aap". It exposes all tools at
# /mcp and subsets at /mcp/<toolset>; the server name is "aap" on every endpoint.
# Toolset membership is recorded in comments below — it determines which endpoint
# serves a tool, but it is not part of the server's identity.
mcpToolDependencies:
  - server: aap
    tools: [
            # system_monitoring
            status_retrieve, mesh_visualizer_retrieve, instances_retrieve,
            instance_groups_list, activity_stream_list, feature_flags_state_retrieve,
            # platform_configuration
            config_retrieve, execution_environments_list,
            controller-settings_list, settings_retrieve, gateway-settings_list,
            # job_management
            jobs_list, projects_list, metrics_retrieve, activation_instances_list,
            # inventory_management
            inventories_list, hosts_list,
            # security_compliance
            credentials_list,
            # user_management
            me_list]

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

This skill follows a 4-step workflow: trigger → gather → analyze → report. All operations are read-only via the AAP MCP Server. It also supports an optional local baseline workflow for recording platform state before a change and comparing a later health check against it.

## Baseline and Diff Mode

### Purpose

Baseline mode turns point-in-time reports into an auditable before/after record. An administrator can:

1. Run a health check and record a normalized local snapshot.
2. Make an approved AAP change outside this skill.
3. Run the same health check again.
4. Compare the new snapshot with the recorded baseline and review expected and unexpected changes.

Baseline mode never writes to AAP. It writes only the locally requested report and snapshot artifacts. If the runtime cannot persist local files, return the normalized snapshot and diff in the response instead.

### Baseline inputs

| Input | Values | Meaning |
|---|---|---|
| `baseline_action` | `none`, `record`, `compare` | Do not persist state, create a baseline, or compare with a baseline |
| `baseline_ref` | Local path or artifact identifier | Required for `compare`; identifies the baseline snapshot |
| `comparison_scope` | `all`, `topology`, `configuration`, `workloads`, `security` | Limit diff output; default `all` |
| `expected_changes` | Structured list or text | Optional operator description of approved changes |

If `compare` is requested without a readable baseline, stop comparison and report the exact fetch or parse failure. Do not silently create a new baseline or treat the current state as its own baseline.

### Snapshot contract

A recorded snapshot is JSON or equivalent structured data with this envelope:

```json
{
  "schema_version": "1",
  "baseline_id": "2026-10-01T15:49:22Z-car-maap1",
  "observed_at": "2026-10-01T15:49:22Z",
  "target": "carmaap1.lan",
  "aap_version": "4.8.9",
  "mode": "full",
  "tool_results": {
    "requested": 19,
    "succeeded": 19,
    "skipped": [],
    "failed": []
  },
  "state": {}
}
```

`state` contains normalized, non-secret observations grouped by health-check dimension:

- `services`: service names and status.
- `mesh`: node identities, node types, readiness, enabled state, and links.
- `instances`: capacity, consumed capacity, remaining capacity, node state, runner version, and last-seen time.
- `instance_groups`: names, capacity, consumed capacity, remaining capacity, running jobs, and member hostnames.
- `activity`: recent change identifiers, timestamps, operations, object types, and redacted change summaries.
- `configuration`: AAP version, non-secret settings, feature flags, and configuration categories.
- `license`: validity/compliance booleans and time-window classification only; never account, subscription, SKU, pool, or credential identifiers.
- `workloads`: job/project/activation counts and status summaries.
- `resources`: metrics, queue depth, inventory/host counts, and execution-environment metadata without secrets.
- `access`: role and privilege summary without usernames or tokens unless explicitly authorized and redacted.

The snapshot must preserve tool success, skip, and failure state. A partial snapshot is not equivalent to a complete baseline.

### Normalization and redaction

Before comparison:

- Normalize timestamps to UTC and record `observed_at` separately from state values.
- Sort unordered collections by stable human-readable identity.
- Compare instance and group identities by hostname/name, not database IDs.
- Exclude volatile fields such as request URLs, pagination cursors, generated UUIDs, current timestamps, and metric scrape timestamps unless they are the subject of the finding.
- Retain activity timestamps and IDs only for change correlation; do not use them as proof that a change was approved.
- Redact passwords, tokens, private keys, certificate contents, account numbers, subscription IDs, installation UUIDs, and other secrets or commercial identifiers.
- Mark unavailable, permission-denied, stale, and not-collected values explicitly. Do not convert them to `null` and describe them as unchanged.

### Diff rules

Compare normalized state by dimension and emit each difference as:

```text
category | path | change | baseline | current | classification | evidence
```

Use these classifications:

- `ADDED`: identity exists only in current state.
- `REMOVED`: identity existed only in baseline.
- `CHANGED`: identity exists in both states but a comparable value changed.
- `UNCHANGED`: no report entry; retain counts in the summary.
- `UNKNOWN`: comparison blocked by missing, failed, unauthorized, or stale data.

Severity remains independent from change type:

- **CRITICAL:** a change or unknown state affects service availability, database reachability, expired licensing, or all usable capacity.
- **WARNING:** a change reduces capacity, changes topology, introduces failures, or leaves a required comparison incomplete.
- **INFO:** an expected or low-risk change, such as a planned node addition, successful version change, or normal license countdown.

For every `CRITICAL` or `WARNING` diff, state whether it is:

1. `EXPECTED` — matches `expected_changes`.
2. `UNEXPECTED` — not described by the operator.
3. `UNVERIFIED` — possibly related, but intent cannot be established from MCP evidence.

Do not infer operator intent from activity-stream actor fields alone.

### Baseline artifact layout

When local persistence is available, use separate immutable-by-convention artifacts:

```text
<report_root>/aap-platform-health/
  baselines/<target>/<baseline_id>.json
  reports/<target>/<observed_at>-baseline.md
  diffs/<target>/<observed_at>-vs-<baseline_id>.md
```

Never overwrite a baseline. A new baseline gets a new identifier. A comparison report records the baseline path, current observation time, schema version, MCP tool coverage, and optional content hashes. File permissions and retention remain the administrator's responsibility; do not claim tamper-proof audit storage unless the storage system provides it.

### Recording a new baseline

When `baseline_action=record` is selected, follow this sequence:

1. Confirm target, mode, and requested dimensions before collection.
2. Run the selected MCP checks and preserve their success, skip, and failure results.
3. Normalize and redact the result according to the snapshot contract.
4. Generate a new `baseline_id` from UTC observation time plus a sanitized target identifier. Do not reuse an existing ID.
5. Check that the destination does not already contain the proposed ID. On collision, stop and generate a different ID; never overwrite.
6. Write the structured snapshot to `baselines/<target>/<baseline_id>.json`.
7. Write a human-readable point-in-time report to `reports/<target>/<observed_at>-baseline.md`.
8. Compute an optional SHA-256 hash of the normalized snapshot after redaction and include it in both report metadata and the returned result.
9. Return the baseline ID, absolute or resolvable artifact paths, observation time, tool coverage, overall status, and hash when available.

Baseline creation output must be easy to pass to a later run:

```json
{
  "action": "record",
  "baseline_id": "2026-10-02T07:44:12Z-carmaap1-lan",
  "baseline_ref": "baselines/carmaap1.lan/2026-10-02T07:44:12Z-carmaap1-lan.json",
  "report_ref": "reports/carmaap1.lan/2026-10-02T07:44:12Z-baseline.md",
  "observed_at": "2026-10-02T07:44:12Z",
  "status": "HEALTHY",
  "checks": {"requested": 19, "succeeded": 19, "failed": 0, "skipped": 0},
  "snapshot_sha256": "<hash of redacted normalized snapshot>"
}
```

If any required check fails, still preserve the artifact as a partial baseline only when the operator explicitly allows partial baselines. Mark it `partial: true`, list failed checks, and prevent it from being used as a complete comparison baseline without an explicit override.

### Diff report requirements

A comparison report includes:

1. Baseline identity, current observation time, target, AAP versions, mode, and tool coverage.
2. Overall status for baseline and current state.
3. Change summary grouped by `ADDED`, `REMOVED`, `CHANGED`, and `UNKNOWN`.
4. Severity and expectedness for every actionable difference.
5. Detailed per-dimension diffs with baseline and current values.
6. Correlation with relevant activity-stream entries, clearly labeled as observed correlation.
7. Unchanged dimensions and skipped/failed checks.
8. Operator-supplied expected changes and unmatched changes.
9. Recommendations, including whether another post-change check is warranted.

End comparison reports with: *"This assessment is advisory. For production decisions, consult Red Hat support."*

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
| `baseline_action` | String | No | `none`, `record`, or `compare` | `none` |
| `baseline_ref` | String | For compare | Local baseline snapshot path or artifact identifier | — |
| `comparison_scope` | String | No | `all`, `topology`, `configuration`, `workloads`, or `security` | `all` |
| `expected_changes` | List or text | No | Approved changes expected between baseline and current run | — |

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

### Baseline comparison example

```
User: Record a full AAP health baseline before the upgrade.

Agent: Run the full read-only check, normalize and redact the result, and save
       a new local baseline artifact. No AAP configuration changes.

User: Compare current state with baseline /reports/aap-platform-health/baselines/aap-2026-10-01.json.

Agent: Run the same full read-only check, compare normalized state, correlate
       differences with activity records, and report expected, unexpected, and
       unverified changes. The baseline remains unchanged.
```

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| aap-validate-deployment-topology | Complementary — topology checks if supported; health check checks if it's working |
| aap-supportability-assessment | Complementary — health = "is it working?"; supportability = "is it supported?" |
| aap-pre-upgrade-readiness | Sequential — if health check recommends an upgrade, pre-upgrade assesses readiness |
