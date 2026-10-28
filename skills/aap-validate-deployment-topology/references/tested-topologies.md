# Tested Deployment Models & Validation Checks

This file contains the detailed topology definitions and validation checks
for the Validate Deployment Topology skill. Applied in Step 3.

> These definitions reflect AAP 2.5/2.6 tested models as of 2026-04-09.
> Always prefer fetching the live "Tested deployment models" guide.

## Tested Deployment Models (AAP 2.5+)

3 deployment modes × 2 scale tiers:

| ID | Name | Mode | Tier | Infrastructure | Key Components |
|----|------|------|------|----------------|----------------|
| `cont-a-env-a` | Container Growth | Containers (Podman) | Growth | **1 VM** | All components on single VM |
| `cont-b-env-a` | Container Enterprise | Containers (Podman) | Enterprise | **13 VMs** | 2 Gateway, 2 Controller, 2 Hub, 2 EDA, 1 hop, 2 exec, external DB, HAProxy LB |
| `ocp-a-env-a` | Operator Growth | OpenShift | Growth | **SNO cluster** (32GB/16CPU/128GB) | All pods on Single Node OpenShift |
| `ocp-b-env-a` | Operator Enterprise | OpenShift | Enterprise | **ROSA HCP** (3 primary + 2 worker) | External DB/Redis/S3, mesh ingress pods |
| `rpm-a-env-a` | RPM Growth | RPM (deprecated) | Growth | **6 VMs** | 1 Gateway, 1 Controller, 1 Hub, 1 EDA, 1 exec, 1 managed DB |
| `rpm-b-env-a` | RPM Enterprise | RPM (deprecated) | Enterprise | **13 VMs** | 2 Gateway, 2 Controller, 2 Hub, 2 EDA, 1 hop, 2 exec, external DB, HAProxy LB |

> RPM installer is deprecated in 2.5 and removed in 2.7.

## Validation Check Details

### 3a. Topology Match

1. **Detect deployment mode:** `IS_K8S` flag from `config_retrieve` — if true → Operator. If false → determine Container vs. RPM from infrastructure signals.
2. **Detect scale tier:** Match component counts against Growth vs Enterprise specs.
3. **Classify:**
   - Exact match → PASS with topology ID
   - Partial match (same mode, between Growth/Enterprise) → WARN with closest match and deviations
   - No match → classify as custom/untested
   - RPM on 2.5+ → WARN "deprecated, removed in 2.7"

### 3b. Node Type Validation

- Control nodes running only control workloads (execution disabled)?
- Execution nodes correctly isolated from control plane?
- Hop nodes positioned correctly (between sites, not running workloads)?
  Hop nodes cannot execute automation — flag if workloads assigned.
- Hybrid nodes are the **default** control plane type per Red Hat docs.
  Adding dedicated control nodes is recommended for scaling, but hybrid
  at scale is not unsupported.

### 3c. Instance Group Capacity Assessment (Advisory)

> These thresholds are advisory. Red Hat does not publish them.

**Capacity metrics per group:**

| Metric | Source |
|--------|--------|
| `capacity` | `instance_groups_list` — total capacity units |
| `consumed_capacity` | `instance_groups_list` — currently used |
| `percent_capacity_remaining` | `instance_groups_list` — available % |
| `jobs_running` | `instance_groups_list` — active jobs |
| `jobs_total` | `instance_groups_list` — historical count |

**Checks:**

| Check | Logic | Severity |
|-------|-------|----------|
| Critical capacity * | `percent_capacity_remaining` < 10% | CRITICAL |
| Low capacity * | `percent_capacity_remaining` < 25% | WARNING |
| Empty group | 0 member nodes | WARNING |
| Orphan nodes | Nodes not in any group | WARNING |
| Unbalanced load * | One group >80% while others <20% | WARNING |
| Idle group * | 0 `jobs_running` AND unchanged `jobs_total` for 7+ days | INFO |

**Additional structural checks:**
- Default instance group overloaded (all workload funneled there)?
- Container groups with valid credentials?
- `max_concurrent_jobs` / `max_forks` configured appropriately?

### 3d. Mesh Topology Validation

- Receptor connections forming a connected graph (no isolated nodes)?
  Ref: `ref-mesh-minimum-resilient-config.adoc`
- Hop nodes correctly between control and remote execution nodes?
- Redundant mesh paths for resilience?
- Direct connections that should go through hop nodes? (advisory)

### 3e. HA Configuration

- Multiple control nodes? → HA candidate
- External database? (required for HA per enterprise topologies)
- HAProxy load balancer? (enterprise topologies require it on ports 80/443;
  LLM cannot verify via MCP — flag as documented requirement)
- Single points of failure?

### 3f. Version Compatibility

- Topology compatible with detected AAP version?
- If `target_version` specified, compatible after upgrade?
- Deprecated topology patterns for target version?
- All nodes same AAP version? Mixed → WARN (may indicate incomplete upgrade)

## Contextual Analysis Guidelines

The LLM should synthesize these signals:
- Single control + 50+ execution nodes → bottleneck recommendation
- No hop nodes between distant execution sites → latency risk
- Mixed-version nodes → possible incomplete upgrade
- Dramatically uneven instance group capacity → workload routing issue
- Standalone controller with external DB → preparation for future HA
- Control nodes high utilization, execution nodes low → routing misconfiguration
- Hop nodes with workload assignment → misconfigured receptor mesh
- Groups at <25% remaining → scaling or redistribution needed
- Groups with 0 jobs_total → misconfigured or unused
