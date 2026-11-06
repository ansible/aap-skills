# Upgrade Path Matrices & Version-Specific Rules

This reference contains version-specific upgrade paths, deprecated features,
and compatibility matrices. Read this file when assessing upgrades to specific
AAP versions.

## 1. Upgrade Paths to AAP 2.6

### Supported Paths

| Source Version | Deployment Type | Target | Path | Notes |
|----------------|-----------------|--------|------|-------|
| RPM 2.4 on RHEL 9 | RPM | 2.6 on RHEL 9 | DIRECT | Must be on latest 2.4 patch |
| RPM 2.4 on RHEL 8 | RPM | 2.6 on RHEL 9 | BACKUP/RESTORE | Backup on RHEL 8, restore to RHEL 9 first |
| RPM 2.5 on RHEL 9 | RPM | 2.6 on RHEL 9 | DIRECT | Must be on latest 2.5 patch |
| RPM 2.5 on RHEL 8 | RPM | 2.6 on RHEL 9 | BACKUP/RESTORE | Backup on RHEL 8, restore to RHEL 9 first |
| Container 2.5 | Container | 2.6 | DIRECT | Must be on latest 2.5 patch |
| Container 2.4 | Container | 2.6 | NOT SUPPORTED | 2.4 container was tech preview |
| Operator 2.4 | Operator | 2.6 | DIRECT | Must be on latest 2.4 patch |
| Operator 2.5 | Operator | 2.6 | DIRECT | Must be on latest 2.5 patch |

Only 2.4 and 2.5 are documented source versions. Older → unsupported.

### Status Evaluation

| Scenario | Status | Action |
|----------|--------|--------|
| Path listed as DIRECT | PASS | Direct upgrade supported |
| Path requires BACKUP/RESTORE | WARN | Must backup/restore to RHEL 9 first |
| Path NOT SUPPORTED | FAIL | Upgrade not supported |
| Source older than 2.4 | FAIL | No documented path |
| Current equals target | INFO | Already at target version |
| Current newer than target | FAIL | Downgrade not supported |

## 2. Database Requirements

**NOT available via MCP.** Customer must verify manually.

### AAP 2.6 Requirements

- Managed databases: PostgreSQL 15
- External databases: PostgreSQL 15, 16, or 17 (must support ICU)
- PostgreSQL 16/17: must use external backup/restore processes

### Manual Check

```bash
psql --version
grep postgresql /etc/ansible/inventory
```

## 3. Deprecated Features (2.5→2.6)

| Feature | Status | Action |
|---------|--------|--------|
| Service-specific APIs (Controller `/api/v2/`, Hub, EDA) | Deprecated | Migrate to Gateway API |
| RPM installer | Deprecated | Removed in 2.7; plan containerized migration |
| `cisco.asa` in `ee-supported` | Removed | Add to custom EE if needed |
| `ibm.qradar` in `ee-supported` | Removed | Add to custom EE if needed |
| `ansible.controller`/`.hub`/`.eda` collections | Deprecated | Replace with `ansible.platform` |
| ServiceNow Notification Service | Deprecated | Will not support Zurich+ |

### Status Evaluation

| Scenario | Status |
|----------|--------|
| No deprecated settings in use | PASS |
| Deprecated settings detected, still functional | WARN |
| Deprecated settings removed in target | FAIL |

## 4. EE Compatibility

**Available via MCP:** Image name, registry, managed flag.
**NOT available:** Internal Python/ansible-core versions.

### EE Lifecycle Policy

EE support tied to ansible-core version lifecycle. EEs using ansible-core
in Full Support or Maintenance phase are supported. EOL → requires rebuild.

### Known 2.6 EE Changes

- `cisco.asa` removed from `ee-supported`
- `ibm.qradar` removed from `ee-supported`
- Custom EEs should target ansible-core 2.15+

### Status Evaluation

| Scenario | Status |
|----------|--------|
| All EEs use Red Hat managed images | PASS |
| Custom EEs detected (non-managed) | WARN — plan rebuild and verify |
| EEs using `cisco.asa` or `ibm.qradar` | WARN — removed from `ee-supported` |

## 5. Authentication Migration

### 2.4→2.6 (Critical)

**BLOCKER:** Inspect ALL SAML authenticators for encrypted private keys.
Encrypted keys NOT supported in AAP 2.6. Replace BEFORE upgrading.

**REQUIRED:** Create a local administrator account and verify login before
upgrading (fallback if auth migration fails).

#### Auto-Migration Requirements

| Auth Type | Required Fields |
|-----------|-----------------|
| LDAP | Server URL |
| GitHub/Azure AD | Key AND secret |
| OIDC | Key, secret, AND OIDC endpoint |
| RADIUS/TACACS+ | Host |

#### NOT Auto-Migrated

- LDAP custom certificates (re-establish manually post-upgrade)
- Hub-only users (recreate manually)
- Controller PATs (deprecated; migrate to Gateway PATs)

### 2.5→2.6

No auth migration. Existing configurations continue. EDA users: must reset
passwords (except SSO users).

### Status Evaluation

| Scenario | Status |
|----------|--------|
| 2.4→2.6: SAML with encrypted private key | FAIL — BLOCKER |
| 2.4→2.6: No local admin account | FAIL — BLOCKER |
| 2.4→2.6: Auth config incomplete | WARN |
| 2.4→2.6: LDAP with custom certificates | WARN — not auto-migrated |
| 2.4→2.6: Hub-only users | WARN — not auto-migrated |
| 2.4→2.6: Controller PATs in use | WARN — deprecated |
| 2.4→2.6: All auth configs complete | PASS |
| 2.5→2.6: Any auth config | PASS |

## 6. Topology Changes

### 2.4→2.6 (Critical — New Infrastructure Required)

- Gateway node(s) with colocated Redis
- Hub node(s) (if not already separate)
- EDA node(s) (if using EDA)
- Network ports for Gateway
- `CSRF_TRUSTED_ORIGIN` if using load balancer
- Centralized Redis (6 VMs for HA)

### 2.5→2.6

No infrastructure changes. Gateway already present.

### Status Evaluation

| Scenario | Status |
|----------|--------|
| 2.4→2.6: Gateway not provisioned | FAIL — BLOCKER |
| 2.4→2.6: Gateway planned/provisioned | WARN — verify ports, Redis |
| 2.5→2.6: Any topology | PASS |

## 7. Custom Content Risk (Advisory)

> Red Hat does not publish custom content risk thresholds.

| Custom Content Count | Risk |
|---------------------|------|
| 0 custom items | LOW — standard platform |
| 1-5 custom items | MEDIUM — verify each item |
| 6-20 custom items | HIGH — significant testing required |
| 20+ custom items | VERY HIGH — dedicated testing phase |

## 8. Operational Readiness

| Check | Status | Action |
|-------|--------|--------|
| No running jobs | PASS | Safe to begin |
| Running jobs detected | WARN | Wait for completion or cancel |
| Active schedules | WARN | Disable before upgrade window |
| Recent backup available | PASS | Rollback path available |
| No recent backup | FAIL | Create backup first |

## 9. Additional 2.4→2.6 Considerations

### RHEL Version (RPM Only)

AAP 2.6 RPM requires RHEL 9.4+. RHEL 8 not supported.

| Scenario | Status |
|----------|--------|
| RPM on RHEL 9.4+ | PASS |
| RPM on RHEL 8 | FAIL — BLOCKER |
| Container or Operator | INFO — not applicable |

### EDA 2.4 Incompatibility

EDA 2.4→2.6 NOT supported. EDA 2.4 database must be removed first.

| Scenario | Status |
|----------|--------|
| 2.4→2.6: EDA detected | FAIL — BLOCKER |
| 2.4→2.6: No EDA | PASS |
| 2.5→2.6: EDA detected | PASS |

### Nested Team Behavior

During 2.4→2.6, nested teams are flattened to direct mapping.
Review RBAC post-upgrade if using nested teams.

### API Deprecation

Service-specific APIs deprecated in 2.6:
- Controller: `/api/v2/` → Gateway API
- Hub: `/api/automation-hub/` → Gateway API
- EDA: `/api/eda/v1/` → Gateway API

### RPM Installer Deprecation

Deprecated in 2.5, removed in 2.7. Plan migration to containerized.
