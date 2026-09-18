# AAP Skills

Ansible Automation Platform skills for AI agents — structured operational expertise delivered via MCP.

## Overview

This repository contains **AAP platform operations skills** authored as `SKILL.md` files with YAML front matter and structured markdown bodies. Each skill encodes Red Hat operational expertise for a specific AAP platform task and is designed to be served as an MCP Resource from the [AAP MCP Server](https://github.com/ansible/aap-mcp-server).

Skills follow the [Ansible Skill Content Type Definition](docs/content-type-definition.md), a three-layer schema built on [agentskills.io](https://agentskills.io):

1. **agentskills.io base** — standard skill metadata (`name`, `description`, `license`)
2. **Red Hat Skill fields** — MCP tool dependencies, support boundary, category
3. **AAP Operational profile** — risk level, AAP version gating, sensitive data flags

## Repository Structure

```
aap-skills/
├── skills/                          # Skill definitions
│   └── <skill-id>/
│       ├── SKILL.md                 # Skill file (front matter + body)
│       └── references/              # Supporting reference material
├── schema/
│   └── aap-skill-v1.schema.json     # JSON Schema for front matter validation
├── docs/
│   └── content-type-definition.md   # Published content type specification
├── LICENSE                          # Apache-2.0
└── README.md
```

## Skills

| Skill | Category | Risk | Description |
|-------|----------|------|-------------|
| [`aap-platform-health-check`](skills/aap-platform-health-check/SKILL.md) | platform-operations | read-only | Comprehensive health checks across all AAP components with correlated diagnostics |

## Content Type Definition

The [Ansible Skill Content Type Definition](docs/content-type-definition.md) defines the front matter schema, body structure, and validation requirements for AAP skills. It is scoped to AAP platform operations skills today, with a three-layer design that supports future skill families (e.g., Ansible DevTools) without breaking changes.

## Validation

Validate a skill's front matter against the JSON Schema:

```bash
yq --front-matter=extract '.' skills/<skill-id>/SKILL.md \
  | npx ajv validate -s schema/aap-skill-v1.schema.json --strict=false -d /dev/stdin
```

## Distribution

Skills are distributed through two paths:

- **Skills over MCP** — served as MCP Resources (`skill://aap/{id}`) from the AAP MCP Server
- **Compass / Lightforge** — registered as `AiResource` entities in the Red Hat catalog

## License

Apache-2.0. See [LICENSE](LICENSE).
