---
name: aap-effective-access-review
description: |
  Determine what access a specified AAP user or team has and which operations
  their observed RBAC grants appear to allow.

  Use when:
  - reviewing a user's or team's effective AAP access
  - checking whether a target can view, use, change, administer, or execute a resource
  - investigating an RBAC access question without changing permissions

  NOT for: broad RBAC posture or compliance auditing (use a dedicated audit
  workflow instead).
license: Apache-2.0
compatibility: Requires the AAP MCP Server for Ansible Automation Platform 2.5+.
allowed-tools: >-
  status_retrieve me_list users_list teams_list users_teams_list teams_users_list
  organizations_list role_definitions_list role_user_assignments_list
  role_team_assignments_list credentials_list job_templates_list
  workflow_job_templates_list projects_list inventories_list hosts_list
  notification_templates_list authenticators_list authenticator_maps_list
  activity_stream_list
metadata:
  author: Red Hat
  version: "1.0.0"
model: inherit
color: cyan
id: aap-effective-access-review
version: 1.0.0
category: identity-access
mcpToolDependencies:
  - server: aap
    tools:
      - status_retrieve
      - me_list
      - users_list
      - teams_list
      - users_teams_list
      - teams_users_list
      - organizations_list
      - role_definitions_list
      - role_user_assignments_list
      - role_team_assignments_list
      - credentials_list
      - job_templates_list
      - workflow_job_templates_list
      - projects_list
      - inventories_list
      - hosts_list
      - notification_templates_list
      - authenticators_list
      - authenticator_maps_list
      - activity_stream_list
supportBoundary:
  model: red-hat
  dependencies:
    - name: aap-mcp-server
      supportStatus: tech-preview
riskLevel: read-only
sensitiveData: true
aapVersion: ">=2.5"
---

# AAP Effective Access Review

Answer: “What can this AAP user or team access, and what can they do?”

This is a point-in-time, read-only assessment. It reports direct grants,
team-inherited grants, organization and resource scope, and conditional
authenticator-map grants. It separates confirmed access from `Not granted`,
`Not observed`, and `Unknown`.

Do not modify RBAC, launch jobs, or perform permission-testing writes.

## Target handling

Supported targets:

- AAP user.
- AAP team.
- External identity group, only when authenticator-map data and external
  identity evidence are available.

If the user does not name a target, ask which user, team, or group they mean,
then default to the authenticated caller for the current review. State this
default explicitly. Do not silently select another account.

If a name could refer to both an AAP team and an external group, ask for the
target type. Do not treat an AAP team as an LDAP or AD group.

## Collection authority

The minimum role for complete cross-user or cross-team collection is Platform
Auditor (System Auditor in AAP 2.5). System Administrator is an accepted
fallback when broader access is authorized. `Organization Auditor` or a lower
scope is insufficient for a platform-wide conclusion.

Verify with `me_list` that the caller has the required role. Then verify that
required list calls return complete pages and are not filtered or denied. If
the caller cannot collect platform-wide evidence, stop the review and advise
that a Platform Auditor or authorized System Administrator run it. Do not
present a partial review as complete.

## MCP data requirements

| Data | MCP tools | Use |
| --- | --- | --- |
| Instance and connectivity | `status_retrieve` | Hostname/IP and collection status |
| Caller and target users | `me_list`, `users_list` | Identity and caller role |
| Teams and membership | `teams_list`, `users_teams_list`, `teams_users_list` | Inherited access |
| Organizations | `organizations_list` | Organization scope |
| Role model | `role_definitions_list` | Permission semantics |
| Direct grants | `role_user_assignments_list` | User-to-role paths |
| Team grants | `role_team_assignments_list` | Team-to-role paths |
| Resource scope | Resource list tools | Object existence and scope |
| Conditional grants | `authenticators_list`, `authenticator_maps_list` | External identity conditions |
| Change evidence | `activity_stream_list` | Recent grant or revoke context |

Resource tools include `credentials_list`, `job_templates_list`,
`workflow_job_templates_list`, `projects_list`, `inventories_list`,
`hosts_list`, and `notification_templates_list`.

Paginate every list. Record requested, collected, skipped, denied, and failed
calls. An incomplete list cannot prove that access is absent.

## Capability interpretation

Normalize live role permissions into these labels only when role definitions
support the mapping:

| Capability | Meaning |
| --- | --- |
| View | Read an object or its metadata |
| Use | Consume an object in an allowed operation |
| Execute | Launch a job, workflow, or equivalent runtime action |
| Change | Modify object configuration |
| Administer | Manage object and access within scope |
| Delete | Remove an object |
| Assign | Grant or alter access |

Do not infer `Delete`, `Assign`, or execution ability from role names alone.
Use live permission codenames and role definitions. If semantics are unclear,
report `Unknown`.

## Caller-versus-target attribution

Resource responses may expose `user_capabilities` for the authenticated MCP
caller, not the requested target. Never use caller capabilities as evidence of
another user's access.

For a named target, derive access from direct user assignments, target team
membership, team role assignments, organization and resource scope, and
authenticator-map conditions. If MCP has no effective-access or
impersonation-capable read endpoint, mark target-specific capabilities
`Unknown` unless assignment and role-definition evidence proves the result.

A global administrator improves collection visibility. It does not change
caller-versus-target attribution.

## Workflow

### 1. Confirm scope

Resolve target, target type, AAP instance, and observation time. Apply the
default-to-caller rule when no target is supplied.

### 2. Verify authority

Call `status_retrieve` and `me_list`. Capture AAP instance hostname/IP from the
status response. Confirm Platform Auditor or System Administrator. Stop on
insufficient visibility.

### 3. Collect evidence

Collect identity, team membership, direct and team grants, role definitions,
organization scope, resource scope, and authenticator maps. Preserve every
grant path. Do not collapse direct and inherited grants into one unexplained
result.

### 4. Calculate effective access

For users, union direct grants with grants inherited through all collected AAP
teams, then apply organization and resource scope. For teams, report team
grants and reachable resources; do not claim what individual members can do
unless membership was collected. Mark authenticator-map access conditional
unless external identity attributes are confirmed.

### 5. Classify negative results

- **Not granted:** evaluated grant paths are complete and the grant is absent.
- **Not observed:** no activity was found; this says nothing about permission.
- **Unknown:** visibility, role semantics, external identity, or collection is incomplete.

Never claim absolute inability unless all relevant grant paths and role
semantics are complete for the stated scope. Do not launch a job to test access.

### 6. Report

Follow [`context/output-format.md`](../../context/output-format.md) for report
structure, MCP quick reference, and standard footer. Include:

1. Executive answer.
2. Target and AAP instance hostname/IP.
3. Visibility and evidence completeness.
4. Effective access matrix.
5. Direct and inherited grant paths.
6. Evaluated non-grants.
7. Unknowns, denied calls, and collection gaps.
8. Observation time and security notes.

State that conclusions describe observed grants, not proof of successful
execution. Flag output as restricted security data.

## External access

AAP user and team review needs no external source beyond the authenticated AAP
MCP Server. External identity-group review requires read-only LDAP, AD, or IdP
access to confirm group membership and nested groups. Required access may
include directory read scope, IdP API access, or SSO-admin approval; do not
assume those permissions exist.

Red Hat documentation can clarify version-specific role semantics or hardening
guidance. Record title, URL, version/date, and access status. Public product
documentation may be available without login, while subscription, SSO, or
customer-only material may require Red Hat authentication. External sources
are optional for an AAP-only access calculation.

## Boundaries

- Point-in-time assessment, not real-time monitoring.
- No RBAC writes, remediation, job launch, or active permission test.
- No compliance conclusion from MCP data alone.
- No external-group conclusion without identity-provider evidence.
- No credential values, tokens, passwords, private keys, or secret fields in output.
