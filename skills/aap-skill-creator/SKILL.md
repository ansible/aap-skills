---
name: aap-skill-creator
description: |
  Create or update AAP Skills that conform to this repository's content type,
  MCP integration rules, evidence requirements, and validation checks.

  Use when:
  - creating a new skill for `ansible/aap-skills`
  - converting an operational procedure into an AAP Skill
  - reviewing or restructuring an existing `SKILL.md`

  NOT for: executing an AAP operation or validating a live platform (use the
  relevant operational skill and AAP MCP Server instead).
license: Apache-2.0
compatibility: Requires access to this repository's content type definition and validation scripts.
allowed-tools: ""
metadata:
  author: Red Hat
  version: "1.0.0"
model: inherit
color: cyan
id: aap-skill-creator
version: 1.0.0
category: authoring
mcpToolDependencies: []
supportBoundary:
  model: red-hat
  dependencies: []
riskLevel: read-only
sensitiveData: false
aapVersion: ">=2.5"
---

# AAP Skill Creator

Create focused, portable skills for this repository. The output is a proposed
`SKILL.md` and any narrowly justified supporting references. This skill does
not call AAP, modify a platform, or submit a pull request.

## Inputs to establish first

Capture these decisions before drafting:

| Input | Required decision |
| --- | --- |
| Skill name | Lowercase `aap-<kebab-case-name>` directory and matching `name`/`id` |
| User outcome | What request the skill handles and what it leaves to another skill |
| Scope | AAP components, versions, and read-only/write/destructive boundary |
| MCP coverage | Exact server and tools the workflow will call |
| Data sources | MCP responses, repository references, and external documentation |
| Sensitive data | Credentials, PII, audit data, or other restricted output |
| Evidence baseline | Tables, thresholds, support policy, recommendations, or version matrix |
| Report format | Whether output uses `context/output-format.md` |

If the requested outcome is ambiguous, narrow scope before creating files. Do
not turn a one-off investigation or unsupported assumption into a universal
skill rule.

## Repository contract

Follow [`docs/content-type-definition.md`](../../docs/content-type-definition.md)
for frontmatter and body requirements. For AAP platform skills, preserve the
three layers:

1. **agentskills.io:** `name`, `description`, `license`, and optional runtime fields.
2. **Red Hat skill:** `id`, semantic `version`, `category`,
   `mcpToolDependencies`, and `supportBoundary`.
3. **AAP operational profile:** `riskLevel`, `sensitiveData`, and `aapVersion`.

Use an existing skill as a structural reference, but copy only patterns that
fit the new scope. Do not invent required fields, MCP tools, role names,
thresholds, or product support claims.

## MCP and access design

- Use AAP MCP Server tools as the exclusive platform integration point.
- Declare every called tool in `mcpToolDependencies`, grouped by server.
- Keep `allowed-tools` empty or consistent with the canonical dependency list.
- Check that each declared tool exists in the target MCP toolset before claiming coverage.
- Map each workflow step to the data it needs and the RBAC permission that gates it.
- Mark `riskLevel: read-only` unless the skill intentionally previews and executes writes.
- Set `sensitiveData: true` for credentials, PII, security audit data, or equivalent restricted data, even when operations are read-only.
- Separate unavailable access from an empty result. Report skipped or denied checks with their cause.
- Never store credentials, tokens, or credential-bearing URLs in skill files or reports.

If an MCP tool cannot supply required data, identify the missing tool or
external source. Do not silently replace it with direct API, CLI, or SSH access.

## Evidence and references

Separate documented facts, live observations, inferred findings, and unknowns.
For external material, record the source title, direct URL, version or date,
access requirement, and what decision it supports.

Use `references/` for substantial or version-sensitive material, such as:

- support and lifecycle tables
- compatibility or feature matrices
- severity thresholds and advisory baselines
- recommendation catalogs
- external-source consultation rules

Prefer authoritative Red Hat documentation for product behavior and lifecycle.
State when authentication, an active subscription, SSO, a support case, TAM,
or another external entitlement is required. Do not treat a source as public
until access has been checked.

## Workflow and output

Write the workflow as observable steps:

1. Verify prerequisites and confirm scope.
2. Gather only the declared data.
3. Analyze against documented or explicitly advisory baselines.
4. Classify limitations and confidence.
5. Produce the expected output with evidence and recommendations.

For report-generating skills, follow
[`context/output-format.md`](../../context/output-format.md). Include the
standard MCP quick reference when tools were called and the standard footer.
For write or destructive skills, include preview, explicit confirmation, and
RBAC enforcement gates.

## Validation gate

Before handoff:

```bash
make install
make validate
```

Confirm that:

- frontmatter parses and required fields are present;
- directory name matches `name` and `id`;
- version is semantic versioning;
- internal Markdown links resolve;
- declared dependencies reflect actual MCP calls;
- scope and risk boundaries are explicit;
- no secrets or customer data were added;
- live validation status and unverified checks are documented.

`aap-skill-creator` is authoring-only, so it intentionally declares no runtime
MCP tools. The repository validator still requires the shared dependency field;
do not copy this empty declaration into an operational skill.
