# Ansible Skill Content Type Definition v1.0

---

## 1. Overview

An **Ansible Skill** is a `SKILL.md` file with YAML front matter and a structured markdown body. A single file serves all distribution paths, such as:

- **Skills over MCP** — an MCP Server parses front matter, serves the file as an MCP Resource at `skill://ansible/{id}`
- **Lightforge / Compass** — the agentskills.io linter validates base fields, Lightforge publishes to external marketplaces, Compass registers the skill as `kind: AiResource`
- **External agents** — Claude Code, Copilot, and other AI agents consume the file directly

This version of the content type definition covers **AAP platform operations skills** — the first skill family published through the AAP MCP Server. The front matter schema uses a **three-layer stack** (agentskills.io base → Red Hat Skill fields → product-specific profile) designed so that future skill families (e.g., Ansible DevTools, content authoring) can adopt the same content type by defining their own profile layer, without breaking changes to the base or Red Hat Skill layers.

This document defines the front matter schema, body structure expectations, and the AAP Operational profile.

---



## 2. Front Matter Schema

Front matter fields are organized into four tiers. A valid Ansible Skill includes all required base fields and Red Hat Skill fields. Skills targeting the AAP platform additionally include AAP operational fields.

```yaml
---
# ─── agentskills.io Base Fields ─────────────────────────────────────────────
#     These fields satisfy the agentskills.io specification. A valid Ansible
#     Skill is also a valid agentskills.io skill — extra fields are ignored
#     by the base linter. See: https://agentskills.io/specification

name: <string>                    # REQUIRED. kebab-case machine identifier.
                                  # 1-64 chars, [a-z0-9-], no consecutive --, no leading/trailing -.
                                  # Must match containing directory name.
description: |                    # REQUIRED. Max 1024 characters. Must include:
  <summary line>                  #   - 1-2 sentence summary of what the skill does
                                  #   - "Use when:" block with 3+ trigger phrases
  Use when:                       #   - "NOT for:" with alternative skill or approach
  - "<trigger phrase 1>"
  - "<trigger phrase 2>"
  - "<trigger phrase 3>"

  NOT for: <anti-pattern> (use <alternative> instead).
license: <spdx-id>               # REQUIRED (Red Hat policy). SPDX identifier (e.g., Apache-2.0).
                                  # agentskills.io marks this optional; Red Hat policy promotes it
                                  # to required at the Red Hat Skill layer (applies to all BUs).
compatibility: <string>           # OPTIONAL. Max 500 characters. Environment requirements.
                                  # Example: "Requires the AAP MCP Server for AAP 2.6+"
allowed-tools: <space-separated>  # OPTIONAL. Space-separated MCP tool names this skill invokes.
                                  # agentskills.io marks this experimental.
                                  # Can be generated from mcpToolDependencies (see §2.3).
metadata:                         # OPTIONAL. Arbitrary key-value pairs for tooling.
  author: <string>                # agentskills.io defines as map<string, string>.
  version: "<string>"

# ─── Agent Runtime Hints ────────────────────────────────────────────────────
#     Consumed by specific agent runtimes (Cursor, Claude Code). Not part of
#     the agentskills.io base specification. Ignored by agents that do not
#     recognize them.

model: inherit                    # OPTIONAL. inherit | sonnet | haiku
                                  # Consumed by Cursor/Claude Code for model selection.
color: <color>                    # OPTIONAL. cyan | green | blue | yellow | red | magenta
                                  # Visual risk indicator in Cursor/Claude Code.
                                  #   cyan = read-only, green = additive, blue = reversible,
                                  #   yellow = destructive-recoverable, red = irreversible,
                                  #   magenta = generative/creative

# ─── Red Hat Skill Fields (Required for MCP Serving and Skill Discovery) ───
#     These fields enable MCP serving, cross-domain skill discovery, and
#     structured dependency declaration. They are the shared intermediate
#     layer between the agentskills.io base format and any product-specific
#     profiles (AAP Operational, DevTools, etc.).
#
#     These fields are also designed for Compass AiResource registration,
#     should that become a distribution requirement.

id: <string>                      # REQUIRED. Same value as `name`. Used for URI:
                                  #   skill://ansible/{id}
version: <semver>                 # REQUIRED. Semantic version (e.g., 1.0.0).
                                  # MCP Resources always serve latest; marketplace tracks versions.
category: <string>                # REQUIRED. Open taxonomy — not a closed enum.
                                  #   AAP values: platform-operations | identity-access |
                                  #     security-intelligence | configuration-management |
                                  #     provisioning | compliance
                                  #   Future profiles define their own values.
                                  #   Avoid generic terms (e.g., "general").

mcpToolDependencies:              # REQUIRED. Canonical declaration of MCP tools used.
  - server: <mcp-server-name>     # Groups tools by their MCP server.
    tools: [<tool1>, <tool2>]     # Tool names must exist on the declared server.

supportBoundary:                  # REQUIRED.
  model: <string>                 # Who backs this skill: "red-hat", "partner", "community".
  dependencies:                   # Per-dependency status. Each entry must declare at
                                  # least one of certificationStatus or supportStatus.
    - name: <dependency-name>
      certificationStatus: <certified | validated | community>
                                  # OPTIONAL. Certification tier for Ansible Content
                                  # Collections (Automation Hub / Galaxy NG).
      supportStatus: <ga | tech-preview | dev-preview>
                                  # OPTIONAL. Red Hat product lifecycle stage for
                                  # product components (APIs, MCP servers, services).

# ─── AAP Operational Profile (Required for AAP Platform Skills) ────────────
#     These fields are required when the skill targets the AAP platform.
#     They enable RBAC filtering and version gating.
#     Skills outside the AAP operational profile omit these entirely.

riskLevel: <string>               # REQUIRED. One of:
                                  #   read-only | write | destructive
                                  # Informs RBAC gating and human-in-the-loop enforcement.
sensitiveData: <boolean>          # OPTIONAL. Default: false.
                                  # true when the skill accesses credentials, PII, security
                                  # audit logs, or other high-sensitivity data — even if the
                                  # skill is read-only. Triggers additional HITL checkpoints
                                  # (see §3.3.2).
aapVersion: "<semver-range>"      # REQUIRED (AAP). Minimum AAP version (e.g., ">=2.5").

# ─── Optional AAP Fields ───────────────────────────────────────────────────

publisher:                        # OPTIONAL. For partner/ecosystem skills.
  name: <string>                  # e.g., "ServiceNow", "CyberArk"
  icon: <url>
  supportUrl: <url>
  collection: <string>            # Partner's certified collection FQCN
---
```



### 2.1 agentskills.io Base Fields

These fields satisfy the [agentskills.io specification](https://agentskills.io/specification). Red Hat policy promotes `license` from optional to required at the Red Hat Skill layer (§2.3).


| Field           | Required             | Type   | Constraints                                       | Consumed By           |
| --------------- | -------------------- | ------ | ------------------------------------------------- | --------------------- |
| `name`          | Yes                  | string | kebab-case, 1-64 chars, matches directory name    | All paths             |
| `description`   | Yes                  | string | Max 1024 chars, includes `Use when:` / `NOT for:` | All paths             |
| `license`       | Yes (Red Hat policy) | string | SPDX identifier                                   | All paths             |
| `compatibility` | No                   | string | Max 500 chars, environment requirements           | Agents, marketplace   |
| `allowed-tools` | No                   | string | Space-separated MCP tool names                    | agentskills.io linter |
| `metadata`      | No                   | map    | String keys → string values                       | Tooling               |


`allowed-tools` **relationship to** `mcpToolDependencies`**:** Both declare which MCP tools the skill uses. `mcpToolDependencies` is the canonical, typed declaration (grouped by server). `allowed-tools` is a flat compatibility field. Authors MAY generate `allowed-tools` by extracting all tool names from `mcpToolDependencies` and joining with spaces. If both are present, `mcpToolDependencies` takes precedence.

### 2.2 Agent Runtime Hints

These fields are consumed by specific agent runtimes. They are not part of the agentskills.io specification and are ignored by agents that do not recognize them.


| Field   | Required | Type | Constraints | Consumed By |
| ------- | -------- | ---- | ----------- | ----------- |
| `model` | No       | enum | `inherit`   | `sonnet`    |
| `color` | No       | enum | `cyan`      | `green`     |


**Recommendation for read-only skills:** `model: inherit`, `color: cyan`.

### 2.3 Red Hat Skill Fields (Required for MCP Serving and Skill Discovery)

These fields are required for MCP serving, structured dependency declaration, and cross-domain skill discovery.


| Field                 | Required | Type   | Constraints                                                                               | Consumed By                                         |
| --------------------- | -------- | ------ | ----------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `id`                  | Yes      | string | Same as `name`; used for `skill://ansible/{id}` URI                                       | MCP Server, marketplace                             |
| `version`             | Yes      | string | Semver (MAJOR.MINOR.PATCH)                                                                | MCP Server, marketplace                             |
| `category`            | Yes      | string | Open taxonomy (see values by domain below). Avoid generic terms.                          | MCP Server (grouping), marketplace (faceted search) |
| `mcpToolDependencies` | Yes      | array  | Server-grouped tool lists (min 1 server)                                                  | MCP Server (validation, RBAC)                       |
| `supportBoundary`     | Yes      | object | Model (`red-hat` / `partner` / `community`) + per-dep certification and/or support status | MCP Server, marketplace (trust badge)               |




#### `category` values

`category` is an open taxonomy — not a closed enum. Each profile defines its own values.


| Domain              | Category Values                                                                                                             |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| AAP (operational)   | `platform-operations`, `identity-access`, `security-intelligence`, `configuration-management`, `provisioning`, `compliance` |
| *(future profiles)* | Values should be kebab-case, 2-3 words, and domain-specific enough to be useful in faceted search.                          |




#### `supportBoundary`

`supportBoundary.model` declares who maintains the skill:


| Value       | Meaning                                               |
| ----------- | ----------------------------------------------------- |
| `red-hat`   | Maintained by Red Hat                                 |
| `partner`   | Maintained by a partner (see `publisher` for details) |
| `community` | Community maintained                                  |


Red Hat-authored AAP operational skills use `red-hat`.

Each entry in `supportBoundary.dependencies` must declare at least one of two status fields:


| Field                 | Applies to                                     | Allowed values                        |
| --------------------- | ---------------------------------------------- | ------------------------------------- |
| `certificationStatus` | Ansible Content Collections (Hub / Galaxy NG)  | `certified`, `validated`, `community` |
| `supportStatus`       | Red Hat product components (APIs, MCP servers) | `ga`, `tech-preview`, `dev-preview`   |


A dependency may declare both when applicable (e.g., a certified collection shipping as part of a Technology Preview feature).

### 2.4 AAP Operational Profile (Required for AAP Platform Skills)

These fields are required when the skill targets the AAP platform. They enable RBAC filtering and version gating. Skills outside this profile omit them entirely.


| Field           | Required | Type    | Constraints                    | Consumed By                           |
| --------------- | -------- | ------- | ------------------------------ | ------------------------------------- |
| `riskLevel`     | Yes      | enum    | `read-only`                    | `write`                               |
| `sensitiveData` | No       | boolean | Default `false`                | MCP Server (HITL enforcement), agents |
| `aapVersion`    | Yes      | string  | Semver range (e.g., `">=2.5"`) | MCP Server (version filtering)        |




#### Confirmation behavior by risk level

The `riskLevel` field determines how the agent should confirm actions with the user. Skill authors should encode these patterns in their workflow steps:


| `riskLevel`   | Agent behavior                                                                                        | Workflow guidance                                                    |
| ------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `read-only`   | Proceed through data-gathering without per-step confirmation. Present final report before concluding. | Confirm scope at the start ("I'll check X, Y, Z — proceed?").        |
| `write`       | Present a preview of intended changes and wait for explicit user confirmation before mutating.        | Use a "preview → confirm → execute" pattern for each mutation.       |
| `destructive` | Present full impact summary, confirm, and re-confirm if scope exceeds the initial request.            | Include an impact assessment step and an explicit confirmation gate. |




#### `sensitiveData`

When `true`, the skill accesses credentials, personally identifiable information (PII), security audit logs, or other high-sensitivity data. This flag is **orthogonal to** `riskLevel` — a skill can be `read-only` yet still handle sensitive data (e.g., listing credential metadata, querying authentication audit trails). The flag triggers additional HITL checkpoints described in §3.3.2 regardless of risk level.

Default is `false`. Omitting the field is equivalent to `false`.



### 2.5 Optional AAP Fields


| Field       | Type   | Default | Purpose                                                     |
| ----------- | ------ | ------- | ----------------------------------------------------------- |
| `publisher` | object | null    | Partner/ecosystem branding + certified collection reference |


#### `publisher`

An optional object identifying the publisher of a partner or ecosystem skill. Contains `name` (e.g., "ServiceNow", "CyberArk"), `icon` (URL to publisher branding), `supportUrl` (where users go for help), and `collection` (the certified Ansible collection FQCN that the skill depends on, e.g., `servicenow.itsm`). This field was designed for the anticipated ecosystem where ISV partners author skills that integrate AAP with their own platforms. In that scenario, users browsing a skill marketplace need to know who built and supports a skill, and the platform needs to surface the correct support channel — Red Hat support for Red Hat-authored skills, partner support for partner-authored skills. The `collection` sub-field links the skill to a certified Ansible Content Collection, which is important for support-boundary clarity: a skill may be `validated` by Red Hat, but the underlying collection has its own certification status. For Red Hat-authored skills shipped in the core repository, this field is typically omitted.

---

## 3. Body Structure

The markdown body follows the [agentskills.io specification](https://agentskills.io/specification) principle: *"There are no format restrictions. Write whatever helps agents perform the task effectively."*

**All Ansible Skills** must include a `# <Skill Title>` heading and a `## Description` section. Beyond that, write whatever helps the agent perform the task.

**AAP Operational Skills** (those declaring `riskLevel` and `aapVersion`) should additionally include the sections, constraints, and HITL patterns described below.

### 3.1 Recommended Sections (AAP Operational)

Additional sections are permitted. This is a minimum, not a ceiling.

#### 3.1.1 `## Description` — Required

Summary of what the skill does, followed by "When to use this skill" trigger phrases and "What this skill is NOT" anti-patterns. This section mirrors the front matter `description` in prose form and helps agents match the skill to a user request.

#### 3.1.2 `## Prerequisites` — Required

Declare required dependencies in a table — MCP server(s), RBAC role, and any other requirements — along with a verification method for each (e.g., "Call `status_retrieve`").

The first workflow step (`### Step 1`) should verify these prerequisites via the declared tool calls. If a prerequisite fails:

1. **Stop** — make no further tool calls.
2. **Report** — tell the user which prerequisite failed and what is needed (e.g., "AAP MCP Server is unreachable" or "Platform Auditor role required, but current user has Organization Auditor").
3. **Ask** — offer the user options: retry after setup, skip the check, or abort.

Do not silently continue with partial data when a required dependency is unavailable.

#### 3.1.3 `## MCP Tools Used` — Required

A table of every MCP tool the skill invokes — the human-readable companion to the `mcpToolDependencies` front matter field. Include the MCP server name, tool name, and a brief description of what the skill uses it for.

#### 3.1.4 `## Workflow` — Required

Numbered steps using `### Step N: <Action Name>` headings. Each step should include:

- **Purpose** — one sentence describing the step's goal.
- **Operations** — which MCP tools are called and what data is collected. Format is flexible: numbered lists, tables, or prose. Steps may group multiple tool calls or describe LLM reasoning with no tool calls (e.g., analysis steps).
- **Decision points** — conditions that change the workflow path (e.g., "Controller unreachable → stop"). Include at least one decision point per step that can fail.



#### 3.1.5 `## Constraints and Guardrails` — Required

Behavioral boundaries the agent must follow when executing this skill. The section should address **at minimum** the eight concerns listed below, worded in the context of the specific skill. These are not boilerplate sentences to copy verbatim — adapt the language to the skill's risk level, tool surface, and workflow. Skills may add domain-specific constraints beyond these.


| Concern                           | What the skill's section must address                                                                                                               | Example                                                                                                            |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **MCP Server exclusivity**        | All platform operations go through the AAP MCP Server — no direct API calls, CLI tools, or SSH.                                                     | *"All data collection uses the AAP MCP Server. Do not call controller APIs directly or SSH into nodes."*           |
| **Risk-level enforcement**        | How the skill's declared `riskLevel` constrains behavior (e.g., read-only skills never modify configuration; write skills confirm before mutating). | *"This skill is read-only. Never create, update, or delete any platform object."*                                  |
| **Preview-first**                 | The agent shows the user what will be collected or changed before executing.                                                                        | *"Before collecting data, confirm scope with the user: 'I will query status, jobs, and mesh topology — proceed?'"* |
| **No credential storage**         | Credentials flow through the MCP Server's credential framework; the skill never persists or logs them.                                              | *"Do not log, echo, or store credentials. All authentication is handled by the MCP Server."*                       |
| **RBAC respect**                  | The skill honors MCP Server permission enforcement and skips (with a note) any inaccessible resources.                                              | *"If a tool call returns a 403, note the gap in the report and continue with available data."*                     |
| **No external data transmission** | Data stays local to the authenticated session.                                                                                                      | *"Do not send collected data to external services, URLs, or third-party APIs."*                                    |
| **Advisory, not authoritative**   | Reports supplement — do not replace — Red Hat support. Include a disclaimer.                                                                        | *"End the report with: 'This assessment is advisory. For production decisions, consult Red Hat support.'"*         |
| **Reference transparency**        | When the workflow consults a reference file, declare which document was consulted and why.                                                          | *"I consulted advisory-baselines.md to determine severity thresholds for controller latency."*                     |




#### 3.1.6 `## Reference Sources` — Recommended

External documentation the skill consults during execution (e.g., advisory baselines, threshold tables, vendor release notes). Flag when baked-in rules may become stale and should be verified against the source.

#### 3.1.7 `## Expected Inputs` — Recommended

User-configurable parameters the skill accepts — target scope, thresholds, filters, or flags. Document the parameter name, type, default (if any), and what it controls.

#### 3.1.8 `## Expected Outputs` — Recommended

What the skill produces: report format, key sections, severity ratings, summary tables, or recommended next steps. Describe the output structure so users know what to expect and agents know what to generate.

#### 3.1.9 `## Example Usage` — Recommended

A conversational example showing the user trigger and the agent's response. Helps both agents (as a few-shot prompt) and human readers (as a preview of the experience).

### 3.2 Line Budget


| Distribution path                 | Limit                    | Enforcement                                |
| --------------------------------- | ------------------------ | ------------------------------------------ |
| Skills over MCP                   | No hard limit            | Served as MCP Resource; full file returned |
| Lightforge / external marketplace | 500 lines per `SKILL.md` | agentskills.io linter                      |


**Recommendation:** Keep `SKILL.md` to ≤500 lines. Move detailed reference material (assessment matrices, threshold tables, source URL lists) to a `references/` subdirectory:

```
<skill-name>/
├── SKILL.md              # Core skill (≤500 lines)
├── references/           # Loaded by agents on demand
│   ├── baselines.md
│   └── sources.md
└── scripts/              # Optional executable code
```

---



### 3.3 Human-in-the-Loop (HITL) Engagement Model

The `riskLevel` field (§2.4) sets the confirmation *intensity*, and the confirmation behavior table prescribes the agent's high-level pattern. This section gives skill authors concrete guidance on **how to design HITL checkpoints** into workflows so that user oversight is proportional to risk.

#### 3.3.1 Principles

1. **Proportional oversight.** HITL effort scales with risk. A `read-only` skill confirms scope once at the start and presents a final report. A `destructive` skill gates every mutation behind an explicit approval and requires a re-confirmation when the blast radius grows beyond the original request.
2. **Informed consent.** Every confirmation prompt must give the user enough context to make a decision — what will happen, what will be affected, and what will not be reversible. "Proceed?" by itself is insufficient.
3. **User agency.** The user can always abort, narrow scope, or skip a step. Workflows must accommodate these choices without producing an inconsistent state.
4. **Fail-open to the user, not to the action.** When the agent is unsure whether an operation is safe, it stops and asks — it does not guess and proceed.



#### 3.3.2 HITL Checkpoint Patterns by Risk Level

Skill authors should embed these patterns in the `## Workflow` steps, not just reference them in Constraints. The table below maps each risk level to the checkpoints a skill's workflow should include.


| `riskLevel`   | Required HITL Checkpoints                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read-only`   | **Scope confirmation** — before data collection begins, state what will be queried and ask the user to confirm. **Report review** — present the final report as a draft for user review before concluding.                                                                                                                                                                                                                                                                                         |
| `write`       | All `read-only` checkpoints, plus: **Preview gate** — before each mutation (or batch of related mutations), show a preview of the intended change (what, where, current value → new value) and wait for explicit confirmation. **Post-write verification** — after a mutation, verify the result and report success or failure before proceeding.                                                                                                                                                  |
| `destructive` | All `write` checkpoints, plus: **Impact assessment** — present a summary of what will be irreversibly affected (resource counts, dependencies, downstream effects). **Double confirmation** — require a second confirmation if the impact exceeds the scope of the original request (e.g., user asked to remove one host, but the host is in a group with active jobs). **Cool-down prompt** — after presenting the impact assessment, suggest the user take a moment to verify before confirming. |


`sensitiveData: true` **overlay** — When the `sensitiveData` front matter flag is set, the following checkpoints apply **in addition to** the risk-level checkpoints above, at any risk level:

- **Data-access confirmation** — before querying sensitive resources (credentials, PII, audit logs), explicitly state *what categories* of sensitive data will be accessed and obtain user confirmation. Do not silently include sensitive data in a broader query sweep.
- **Redaction by default** — present sensitive values in redacted form (e.g., `*`*** for credential secrets, masked usernames) unless the user explicitly requests unredacted output.
- **No-persist reminder** — remind the user that sensitive data should not be copied into tickets, shared documents, or chat logs without appropriate handling. Include this note in the report output.



#### 3.3.3 Writing HITL into Workflow Steps

When authoring `### Step N` entries in the Workflow section:

- **Make the checkpoint explicit.** Add a decision point such as *"Present the list of changes to the user and wait for confirmation before proceeding to Step N+1."* Do not assume the agent will infer where to pause.
- **Specify what the agent shows.** Describe the information the user needs to see — a table of affected resources, a diff of configuration values, a summary count. The agent cannot present useful confirmation prompts if the skill does not say what to include.
- **Handle rejection.** Each confirmation checkpoint should state what happens if the user says no: skip that step and continue, abort the entire workflow, or narrow scope and retry.
- **Batch where sensible.** For `write` skills that make many small related changes (e.g., updating tags on 20 hosts), a single preview of the full batch is better than 20 individual confirmations. Group related mutations under one gate.



#### 3.3.4 Relationship to Constraints and Guardrails

The `## Constraints and Guardrails` section (§3.1.5) already requires skills to address **Risk-level enforcement** and **Preview-first** behavior. HITL checkpoints are the *mechanism* through which those constraints are enforced. When writing the Constraints section, reference the specific HITL checkpoints defined in the Workflow rather than restating them in abstract terms.

#### 3.3.5 Future: MCP Tasks Extension

Today, all HITL interactions happen synchronously within the agent session — the agent pauses, presents information, and waits for the user's response in the same conversation turn.

The [MCP Tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview) introduces **asynchronous task handles** for long-running operations. When a tool call returns a `CreateTaskResult` instead of an immediate result, the agent receives a durable `taskId` that it can poll for progress. Critically for HITL, a task can enter the `input_required` state, surfacing an input request that the agent (or user) must fulfill before the operation continues.

**What this means for skill design:**

- **Approval gates become first-class protocol.** A `destructive` skill could submit a change request to the AAP MCP Server, which returns a task in `input_required` status. The agent presents the approval prompt to the user. The user's confirmation is sent back via `tasks/update`, and the server proceeds — or the user cancels via `tasks/cancel`.
- **Long-running operations get progress visibility.** Skills that trigger batch operations (e.g., rolling credential rotations, firmware updates across an inventory) can report incremental progress through task status messages, rather than blocking the conversation.
- **Crash resilience.** If the agent session disconnects during a `destructive` operation, the task ID survives. A reconnected session can resume polling without re-executing the operation.

**Guidance for skill authors today:**

- Design workflows as if HITL checkpoints *could* be asynchronous. Structure confirmation gates as discrete, self-contained decision points — not as inline prose that depends on conversational flow.
- Use the `### Step N` pattern to isolate mutations behind clear gates. This structure maps naturally to a future where Step N submits a task and Step N+1 begins only when the task reaches `completed`.
- The AAP MCP Server does not currently implement the Tasks extension. When it does, skills that already follow the checkpoint patterns in §3.3.2 will require minimal changes — the HITL interaction model stays the same; only the transport (synchronous prompt → asynchronous task) changes.

---



## 4. Validation

This section describes how to verify that a finished skill conforms to the content type. Skill authors should run these checks before submitting a skill for review. Reviewers and CI pipelines use the same criteria to accept or reject a skill.

### 4.1 All Ansible Skills

A valid Ansible Skill passes:

1. **agentskills.io linter** (`skills-ref validate`) — base format compliance (name, description, directory name match)
2. **Red Hat Skill field check** — `id`, `version`, `category`, `mcpToolDependencies`, `supportBoundary` present and well-formed
3. **MCP tool reference check** — every tool in `mcpToolDependencies` exists on the declared MCP server



### 4.2 AAP Operational Skills

AAP operational skills additionally pass:

1. **AAP schema validation** — JSON Schema conformance against `schema/aap-skill-v1.schema.json`
2. **Body section check** — all required sections from §3.1 are present



### 4.3 JSON Schema

The machine-readable validation schema lives at `[schema/aap-skill-v1.schema.json](./schema/aap-skill-v1.schema.json)`.

**Scope:**

- Validates all required fields (agentskills.io base + Red Hat Skill + AAP operational) and optional fields.
- Uses JSON Schema 2020-12 draft.
- `additionalProperties` is `false` for the top-level object. Fields not defined in the schema are rejected.

**Usage:**

```bash
yq --front-matter=extract '.' skills/platform-health-check/SKILL.md \
  | npx ajv validate -s schema/aap-skill-v1.schema.json --strict=false -d /dev/stdin
```

---



## 5. Examples



### 5.1 AAP Operational Skill (Read-Only)

```yaml
---
name: platform-health-check
description: |
  Run comprehensive health checks across all AAP components and produce
  an actionable diagnostics report with correlated analysis.

  Use when:
  - "Is my platform healthy?"
  - "Run diagnostics on my AAP"
  - Before or after upgrades to confirm stability

  NOT for: remediation actions (recommend steps but do not execute).
license: Apache-2.0
compatibility: Requires the AAP MCP Server for Ansible Automation Platform 2.5+

model: inherit
color: cyan

id: platform-health-check
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
    - name: aap-controller-api
      certificationStatus: certified
    - name: aap-mcp-server
      supportStatus: tech-preview

riskLevel: read-only
sensitiveData: false
aapVersion: ">=2.5"

---
```



### 5.2 Forward Compatibility — Non-AAP Profiles

The three-layer schema is designed so that future skill families can adopt this content type by defining their own profile layer. A non-AAP skill (e.g., an Ansible DevTools IDE skill) would include the agentskills.io base fields and Red Hat Skill fields, define its own `category` values, and omit the AAP Operational fields (`riskLevel`, `aapVersion`, `publisher`). No changes to the base or Red Hat Skill layers would be required. The body structure requirements from §3 (AAP sections, constraints, HITL table) would not apply — the non-AAP profile would define its own body conventions. See the [Ansible DevTools skills](https://github.com/ansible/vscode-ansible/tree/next/skills) for the primary candidate for a future profile.

---



## 6. References

- [agentskills.io specification](https://agentskills.io/specification) — Base `skill.md` format specification
- [SKILL_DESIGN_PRINCIPLES.md](https://github.com/RHEcosystemAppEng/agentic-plugins/blob/main/SKILL_DESIGN_PRINCIPLES.md) — Body structure standard (v5.0)
- [rh-automation pack](https://github.com/RHEcosystemAppEng/agentic-plugins/tree/main/rh-automation) — Reference implementation of agentskills.io base format
- [IXD-77](https://redhat.atlassian.net/browse/IXD-77) — "Gold Source" Agentic Skills & Tools (guild framework)
- [ANSTRAT-2122](https://redhat.atlassian.net/browse/ANSTRAT-2122) — Ansible Skill Content Type Definition (this feature)
- [ANSTRAT-2123](https://redhat.atlassian.net/browse/ANSTRAT-2123) — AAP Operational Skill Authoring
- [ANSTRAT-2140](https://redhat.atlassian.net/browse/ANSTRAT-2140) — External Marketplace Publishing

**Related — future profile compatibility:**

- [Ansible DevTools skills](https://github.com/ansible/vscode-ansible/tree/next/skills) — IDE skills using agentskills.io base format (candidate for future DevTools profile)
- [ADR-014: Internal Skills as AI Prompt Source](https://github.com/ansible/vscode-ansible/blob/next/.sdlc/adrs/ADR-014-internal-skills-as-prompt-source.md) — Ansible DevTools architecture decision for skill-backed prompts

