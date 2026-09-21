# AAP Skills — Ansible Automation Platform AI Skills

AI agent skills for Ansible Automation Platform (AAP), designed for cross-platform AI agents (Claude Code, VS Code Copilot, Gemini CLI, Cursor).

## What Are AAP Skills?

AAP Skills are structured knowledge packages that enable AI agents to perform AAP platform operations through the AAP MCP Server. Each skill encodes Red Hat's operational expertise into an opinionated, governed workflow — not a generic module wrapper.

**Design principles:**
- **Specialised for Ansible Automation Platform.** Skills operate on AAP-specific functionalities and reference Red Hat's published support matrix and documentation.
- **AAP MCP Server is the exclusive integration point.** All platform operations go through MCP tool invocations. No direct API calls, no `awx` CLI, no SSH. If the MCP Server is down, the skill doesn't work — by design.
- **Default to read-only, human-in-the-loop for write operations.** Skills default to observation and assessment. Write operations require explicit user confirmation and are gated by RBAC as enforced by the MCP Server.
- **Cross-platform by design.** Skills are authored as SKILL.md (the open standard adopted by Claude Code, VS Code, Gemini CLI, and Cursor), portable across AI agent runtimes.

## Skills

### Platform operations (read-only)

| # | Skill | Risk | MCP | Notes |
|---|-------|------|-----|-------|
| 1 | [Platform Health Check](skills/aap-platform-health-check/SKILL.md) | Low (read-only) | Core/Full modes | Service status, mesh topology, capacity, license, EEs, queue depth |

## Content Type Definition

Skills follow the [Ansible Skill Content Type Definition](docs/content-type-definition.md), a three-layer front matter schema built on [agentskills.io](https://agentskills.io):

1. **agentskills.io base** — standard skill metadata (`name`, `description`, `license`)
2. **Red Hat Skill fields** — MCP tool dependencies, support boundary, category
3. **AAP Operational profile** — risk level, AAP version gating, sensitive data flags

The spec is scoped to AAP platform operations skills today, with a three-layer design that supports future skill families (e.g., Ansible DevTools) without breaking changes to the base or Red Hat Skill layers.

## Prerequisites

Skills require the AAP MCP Server to function. All platform operations go through MCP tool invocations exclusively.

| Integration | Type | Required | Purpose |
|-------------|------|----------|---------|
| **AAP MCP Server** | `mcp-server` | **Yes** | All AAP platform operations — the exclusive integration point for every skill |

**Quick check:** Run `status_retrieve` via the MCP Server. If it returns platform component status, you're ready to use any read-only skill.

> **Note:** No additional collections, execution environments, or manual installation steps are required.

## Repository Structure

```
aap-skills/
├── README.md
├── LICENSE                            # Apache 2.0
├── skills/
│   └── aap-{skill-name}/
│       ├── SKILL.md                   # Skill file (front matter + body)
│       └── references/                # Supporting reference material
└── docs/
    └── content-type-definition.md     # Published content type specification
```

### Skill directory contents

Each skill directory contains:

- **`SKILL.md`** — Portable knowledge layer. Contains everything an AI model needs to execute the skill: description, prerequisites, MCP tools, workflow steps, constraints, expected outputs. Works on Claude Code, Copilot, Gemini CLI, Cursor, ChatGPT.
- **`references/`** — Reference content split out to keep SKILL.md lean (threshold tables, source URL lists, compatibility matrices). Loaded by agents on demand during workflow execution.

## Distribution

Skills are distributed through two paths:

- **Skills over MCP** — served as MCP Resources (`skill://aap/{id}`) from the [AAP MCP Server](https://github.com/ansible/aap-mcp-server)
- **Compass / Lightforge** — registered as `AiResource` entities in the Red Hat catalog

## License

Apache 2.0 — See [LICENSE](LICENSE).
