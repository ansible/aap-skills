# Support Matrix Assessment Rules

This file contains the detailed assessment rules for each supportability
dimension. Applied in Step 3 (Cross-Reference Against Support Matrix).

## 1. AAP Version (Time-Based Lifecycle)

### Primary Method — Product Life Cycle Data API

Fetch: `GET https://access.redhat.com/product-life-cycles/api/v1/products?name=Automation+Execution+Environment`

Returns structured JSON with exact phase dates. Match installed version
(e.g., AAP 2.5 → `ansible-automation-platform-25`) and read the `type` field:

- `type` = "Full Support" → PASS
- `type` = "Maintenance Support" (MS1 or MS2) → WARN with upgrade recommendation and phase end date
- `type` = "End of life" → FAIL
- Version not found → INFO ("verify with Red Hat")

### Fallback — Baked-in Phase Model

Red Hat's AAP lifecycle phases after GA date:
- **Full Support** (~first 6 months): Critical/important security, urgent/high bug fixes → PASS
- **Maintenance Support 1** (~months 7-12): Critical security, urgent bugs only → WARN
- **Maintenance Support 2** (~months 13-18): Critical security only → WARN (urgent)
- **End of Life** (after ~month 18): No fixes → FAIL

Do not assume "N-1 = Maintenance" — phase depends on release dates, not version ordinal.

## 2. Deployment Topology

Red Hat documents 6 reference topologies (3 deployment models × 2 sizes):

| Deployment Model | Growth | Enterprise |
|-----------------|--------|-----------|
| RPM (deprecated 2.5, removed 2.7) | Yes | Yes |
| Containerized (Podman) | Yes | Yes |
| Operator (OpenShift) | Yes | Yes |

Assessment rules:
- Matches one of the 6 tested topologies → PASS
- Single-node for dev/testing → PASS with note "not a production topology"
- RPM on AAP 2.5 → WARN "deprecated in 2.5, removed in 2.7"
- Custom hybrid not in planning guide → WARN ("confirm with Red Hat")
- Mixed component versions → FAIL
- Ref: access.redhat.com/articles/7117676, access.redhat.com/articles/7095801

## 3. Database (Extended — Requires CaC Setup)

For AAP 2.6:
- **Managed:** PostgreSQL 15 → PASS
- **External:** PostgreSQL 15, 16, or 17 → PASS (16/17: WARN about backup utilities)
- Outside supported range → FAIL
- Non-PostgreSQL → FAIL
- CaC not available → INFO ("not assessed")

## 4. Collections (Extended — Requires CaC Setup)

- Red Hat Certified (from Automation Hub) → PASS
- Red Hat Validated → PASS or WARN depending on `strict_mode`
- Community (from Galaxy) → WARN "not supported"
- Custom/private → INFO "unknown — verify with vendor"
- Deprecated collections (`ansible.controller`, `.hub`, `.eda`) → WARN "migrate to `ansible.platform`"
- CaC not available → INFO ("not assessed")

## 5. Execution Environments

Three support tiers:
- **Red Hat-provided EEs** (`managed=true`) → PASS (fully supported, auto-updated)
- **Custom EEs on Red Hat base images** (ansible-core 2.16+, Python 3.11+, Ansible Runner) → WARN "Red Hat supports framework and base; custom content is customer's responsibility"
- **Custom EEs on non-Red Hat base images** → FAIL "not supported"

Also check against EE Lifecycle Policy: ansible-core version must be in
Full Support or Maintenance phase. EOL ansible-core = unsupported.

Deprecation note (AAP 2.6): `cisco.asa` and `ibm.qradar` removed from
`ee-supported`. Flag as INFO if present in custom EEs.

## 6. Authentication (Gateway Pluggable Auth — AAP 2.5+)

Supported authenticator types:
- LDAP → PASS
- SAML → PASS
- Generic OIDC → PASS
- Azure AD → PASS
- GitHub (standard, Enterprise, Organization, Team) → PASS
- OAuth 2.0 → PASS
- Local authentication (built-in) → PASS
- Custom auth backends → FAIL

**RADIUS note:** Supported under Controller-native auth (pre-2.5) but NOT listed
in Gateway pluggable auth docs. On AAP 2.5+, classify as WARN.

Assessed via `authenticators_list`.

## 7. External Credential Lookups

Supported plugins (all → PASS):
1. AWS Secrets Manager Lookup
2. Centrify Vault Credential Provider Lookup
3. CyberArk Central Credential Provider (CCP) Lookup
4. CyberArk Conjur Secrets Manager Lookup
5. HashiCorp Vault Key-Value (KV) Store
6. HashiCorp Vault SSH Secrets Engine
7. Azure Key Management System (KMS)
8. Thycotic DevOps Secrets Vault
9. Thycotic Secret Server
10. GitHub App Token Lookup

Custom plugins not in list → WARN "platform supported; plugin is customer's responsibility"

Assessed via `credential_types_list` — distinguish standard (kind=`cloud`, `net`)
from custom (kind=blank/custom) and external (has `injectors` with lookup).

## 8. Deprecated Features

| Deprecated Item | AAP Version | Impact |
|----------------|-------------|--------|
| RPM installer | Deprecated 2.5, removed 2.7 | WARN — plan migration |
| Direct service API access | Being superseded by Gateway APIs | WARN if integrations use direct APIs |
| Service-specific collections | Deprecated after 2.6 → `ansible.platform` | WARN with migration guidance |
| EE collections (`cisco.asa`, `ibm.qradar`) | Removed from ee-supported in 2.6 | INFO |
| ServiceNow Notification | Deprecated for Zurich+ | WARN if detected |

Assessed via `controller-settings_list` (deprecated settings),
`notification_templates_list` (deprecated types),
`mesh_visualizer_retrieve` (topology type).
