---
# ─── agentskills.io Base Fields ─────────────────────────────────────────────
name: aap-validate-deployment-topology
description: |
  Validate the current AAP deployment topology against Red Hat's published
  tested deployment models. Identifies node types, mesh topology, instance
  groups, and HA configuration.

  Use when:
  - "Is this topology supported by Red Hat?"
  - "Validate my AAP architecture"
  - "Check if my deployment matches a tested topology"
  - After adding or removing nodes to verify topology remains supported

  NOT for: topology changes or remediation (recommend steps but do not execute).
license: Apache-2.0
compatibility: Requires the AAP MCP Server for Ansible Automation Platform 2.5+
allowed-tools: >-
  status_retrieve config_retrieve me_list instances_retrieve
  instance_groups_list mesh_visualizer_retrieve instance_groups_retrieve
  metrics_retrieve settings_retrieve
metadata:
  author: Red Hat
  version: "0.1.0"

# ─── Agent Runtime Hints ────────────────────────────────────────────────────
model: inherit
color: cyan

# ─── Red Hat Skill Fields ───────────────────────────────────────────────────
id: aap-validate-deployment-topology
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
      - instance_groups_retrieve
      # platform_configuration
      - config_retrieve
      - settings_retrieve
      # job_management
      - metrics_retrieve
      # user_management
      - me_list

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

# Validate Deployment Topology Against Supported Architectures

Follow [`context/output-format.md`](../../context/output-format.md) for report structure, Markdown formatting, save options, and the standard MCP quick reference and footer.

## Description

Validate the current AAP deployment topology against Red Hat's published tested deployment models from the AAP Planning Guide. Identify node types (control, execution, hop, hybrid), instance group configuration and capacity, mesh topology and receptor network, HA configuration, and whether the topology matches a documented reference architecture.

**When to use this skill:**
- After initial AAP deployment to confirm topology matches a tested architecture
- Before upgrading to verify topology compatibility with the target version
- When adding/removing nodes to verify the topology remains supported
- When investigating performance issues that might be topology-related

**What this skill is NOT:**
- Not a monitoring tool — produces a point-in-time topology validation
- Does not modify topology — all operations are read-only
- Does not replace the AAP Planning Guide — supplements with automated validation

## Prerequisites

### Dependencies

| Dependency | Type | Required | Check |
|------------|------|----------|-------|
| AAP MCP Server | MCP server | Yes | Call `status_retrieve` |

**RBAC:** Requires **Platform Auditor** role (System Auditor in AAP 2.5) or System Administrator.

## MCP Tools Used

This is the most MCP-efficient skill in the portfolio — only 6 core tools plus 2 supplementary.

| Tool | Server | Purpose | Data Returned |
|------|--------|---------|---------------|
| `status_retrieve` | system-monitor | Service health | Component status, HA mode |
| `config_retrieve` | platform-config | Platform config | AAP version, IS_K8S flag |
| `me_list` | user-mgmt | User permissions | Role assignments |
| `instances_retrieve` | system-monitor | Node details | Node type, capacity, utilization |
| `instance_groups_list` | system-monitor | Instance groups | Group config, node assignments, capacity |
| `mesh_visualizer_retrieve` | system-monitor | **Primary topology tool** | All nodes, links, node types |
| `instance_groups_retrieve` | system-monitor | Detailed group info | Capacity, jobs_running, jobs_total |
| `metrics_retrieve` | job-mgmt | Capacity metrics | Instance capacity/consumed, DB connections |
| `settings_retrieve` | platform-config | System settings | IS_K8S flag confirmation |

> **Note:** There is no `instances_list` tool. Use `mesh_visualizer_retrieve` to discover node IDs, then `instances_retrieve` for details. **Only use IDs discovered via `mesh_visualizer_retrieve` — never fabricate IDs.** `instances_retrieve` may hang indefinitely for non-existent IDs.

## Reference Sources

Read `references/red-hat-sources.md` for the full source URL table and consultation protocol.

The **Tested deployment models** guide is THE primary source — it defines what Red Hat tests and supports. The skill applies a two-tier model: (1) live documentation fetch, (2) baked-in topology definitions as fallback.

## Workflow

This skill follows a 4-step workflow: trigger → discover → validate → report. All operations are read-only via the AAP MCP Server.

### Step 1: Verify MCP Server Connectivity and Permissions

**Purpose:** Confirm connectivity and sufficient permissions.

1. `status_retrieve` — verify connectivity, capture AAP version
2. `me_list` — retrieve role assignments
3. Validate Platform Auditor or System Administrator permissions

**Decision point — prerequisite failure:**
- Controller unreachable → **Stop** (make no further tool calls). **Report** which prerequisite failed and what is needed. **Ask** the user: retry after setup, skip the check, or abort.
- Insufficient permissions → report skipped checks, continue with available data.

4. **Scope confirmation (HITL checkpoint):** Present the user with what will be queried — list the MCP tools and topology dimensions to be validated. Wait for explicit confirmation before proceeding to Step 2. If the user narrows scope, adjust accordingly. If the user aborts, stop.

### Step 2: Discover Current Topology

**Purpose:** Build a comprehensive map of the current deployment.

**Operations:**

| MCP Tool | Data Collected |
|----------|----------------|
| `mesh_visualizer_retrieve` | All nodes, types, receptor connections, mesh paths |
| `instances_retrieve` | Per-node detail for each ID from mesh_visualizer |
| `instance_groups_list` | Groups, member nodes, capacity allocation |
| `config_retrieve` | AAP version, IS_K8S flag |
| `status_retrieve` | HA configuration, node health |
| `metrics_retrieve` | Instance capacity/consumed, DB connections |

**Topology map:** Node inventory, instance group membership, mesh connections, HA configuration, platform type (RPM/Container/Operator).

### Step 3: Validate Against Tested Deployment Models

**Purpose:** Compare discovered topology against Red Hat's tested models.

Read `references/tested-topologies.md` for the detailed topology definitions and validation checks.

**Tested Deployment Models (AAP 2.5+):** 3 deployment modes × 2 scale tiers:

| ID | Name | Mode | Tier | Infrastructure |
|----|------|------|------|----------------|
| `cont-a-env-a` | Container Growth | Containers | Growth | 1 VM |
| `cont-b-env-a` | Container Enterprise | Containers | Enterprise | 13 VMs |
| `ocp-a-env-a` | Operator Growth | OpenShift | Growth | SNO cluster |
| `ocp-b-env-a` | Operator Enterprise | OpenShift | Enterprise | ROSA HCP |
| `rpm-a-env-a` | RPM Growth | RPM (deprecated) | Growth | 6 VMs |
| `rpm-b-env-a` | RPM Enterprise | RPM (deprecated) | Enterprise | 13 VMs |

**Validation checks:**
- **3a. Topology Match** — detect mode and tier, match against tested models
- **3b. Node Type Validation** — appropriate roles, control isolation, hop node positioning
- **3c. Instance Group Capacity** — critical/low capacity, empty/orphan groups, unbalanced load
- **3d. Mesh Topology** — connected graph, redundant paths, hop node positioning
- **3e. HA Configuration** — multiple control nodes, external database, load balancer
- **3f. Version Compatibility** — topology compatible with detected/target AAP version

**AI Value-Add — Contextual Topology Analysis:** Single control node with 50+ execution nodes is a bottleneck. Mesh without hop nodes between distant sites has latency risk. Mixed-version nodes may indicate incomplete upgrade. Uneven instance group capacity suggests misconfigured workload routing. The LLM synthesizes these signals into actionable recommendations.

### Step 4: Generate Topology Validation Report

**Purpose:** Produce a structured report with topology diagram, findings, and recommendations.

**Report sections:**
1. Topology overview (node table, mesh link diagram)
2. Reference architecture comparison (matched tested model ID or closest match with deviations)
3. Node configuration validation
4. Capacity analysis (enhanced instance group table with used/available/running/total)
5. Receptor mesh health (connectivity, redundancy, SPOFs)
6. Findings summary table

**Report review (HITL checkpoint):** Present the completed report as a draft for user review before concluding. The user may request adjustments, deeper analysis on specific findings, or additional context before accepting the final report.

**Status values:**

| Status | Criteria |
|--------|----------|
| **VALID** | Matches a tested deployment model; all checks PASS |
| **NEEDS ATTENTION** | Close to a tested model with deviations, or WARN findings |
| **INVALID** | No match to any tested model, or FAIL findings |

## Constraints and Guardrails

1. **MCP Server only.** All operations through the AAP MCP Server. Never call AAP APIs directly, use CLI tools, or SSH.
2. **Read-only operations only.** NEVER modify any AAP configuration.
3. **Preview-first.** Show the user what data will be collected before executing.
4. **No credential storage.** Credentials flow through the MCP Server's credential framework.
5. **RBAC respect.** Honor MCP Server permission enforcement. Skip and note inaccessible resources.
6. **No external data transmission.** Topology data stays local.
7. **Advisory, not authoritative.** Include disclaimer: not an official Red Hat supportability determination. End the report with: *"This assessment is advisory. For production decisions, consult Red Hat support."*
8. **Reference transparency.** When the workflow consults a reference file, declare which document was consulted and why. For example: *"I consulted tested-topologies.md to validate the deployment against Red Hat's tested deployment models."*
9. **Version-aware queries.** Check AAP version before querying version-specific resources.
10. **Topology data is confidential.** Flag reports containing node hostnames, network topology, and infrastructure details.

## Expected Inputs

| Input | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `target_topology` | String | No | Tested topology to validate against | auto-detect |
| `target_version` | String | No | Validate compatibility with a target AAP version | — |

## Expected Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Topology validation report | Structured text | Full topology assessment with diagram and findings |
| Overall status | Enum | `VALID`, `NEEDS_ATTENTION`, or `INVALID` |
| Topology diagram | Text-based | Visual representation of nodes and connections |
| Findings list | Structured data | Each finding with severity and recommendation |
| Recommendations | Structured data | Prioritized remediation actions |

## Example Usage

```
User: Validate the deployment topology of my AAP platform.

Agent: I'll validate your deployment topology using 6 MCP tools (all read-only):
  mesh_visualizer_retrieve, instances_retrieve, instance_groups_list,
  config_retrieve, status_retrieve, me_list.
  No configuration will be changed. Shall I proceed?

User: Yes

Agent:
  Nodes: 5 (2 control, 2 execution, 1 hop) | HA: Enabled | RPM deploy

  Topology:
    [control-1]---[control-2]
         |              |
         +------+-------+
                |
           [hop-dc2]--------[exec-dc2-1]
                              [exec-dc2-2]

  Status: VALID — matches RPM Enterprise (rpm-b-env-a)
  Findings:
  1. [PASS] Matches RPM Enterprise tested deployment model
  2. [PASS] HA configured — 2 control nodes with external DB
  3. [WARN] Single hop node to DC2 — SPOF for remote execution
  4. [WARN] RPM deprecated in 2.5, removed in 2.7 — plan migration
```

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| aap-platform-health-check | Complementary — topology validates if supported; health check validates if working |
| aap-supportability-assessment | Overlapping — supportability includes topology as one of 10 dimensions; this skill goes deeper |
| aap-pre-upgrade-readiness | Sequential — validate current topology, then check compatibility with target version |
