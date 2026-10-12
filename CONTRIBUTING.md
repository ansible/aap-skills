# Contributing to AAP Skills

Thank you for contributing to AAP Skills for Ansible Automation Platform.

## Before you start

- Read the [README](README.md) and [Ansible Skill Content Type Definition](docs/content-type-definition.md).
- Keep changes scoped to this repository. Do not add credentials, tokens, customer data, or environment-specific secrets.
- Use the AAP MCP Server as the integration point for platform operations. Skills do not call AAP APIs directly, use the `awx` CLI, or connect through SSH.

## Create a change

1. Fork `ansible/aap-skills` and create a focused feature branch from `main`.
2. Add or update content under the appropriate repository path.
3. Keep each skill in `skills/aap-<kebab-case-name>/SKILL.md`. The directory name and frontmatter `name` must match.
4. For an AAP platform skill, follow the three-layer frontmatter defined in the content type specification:
   - agentskills.io base fields, including `name`, `description`, and `license`.
   - Red Hat skill fields, including `id`, `version`, `category`, `mcpToolDependencies`, and `supportBoundary`.
   - AAP operational fields, including `riskLevel` and `aapVersion`.
5. Declare every MCP tool used by the skill in `mcpToolDependencies`. Keep `allowed-tools` consistent when it is present.
6. Default platform operations to read-only. Write or destructive workflows need explicit user confirmation, clear impact details, and RBAC enforcement.
7. Put substantial, version-sensitive material in a skill `references/` directory. Keep links relative and verify them locally.
8. For report-generating skills, follow [`context/output-format.md`](context/output-format.md), including the MCP quick reference and standard footer.

## Validate locally

The repository uses Python 3.11 or newer and `uv` for development dependencies.

```bash
make install
make validate
```

`make validate` runs the skill validator and codespell. For a spelling-only check, run:

```bash
make validate-spelling
```

When a change depends on live AAP behavior, test it through the AAP MCP Server when access is available. Record the AAP version, MCP tools exercised, access limitations, and any unverified checks in the pull request. Do not include secrets or sensitive response data.

## Open a pull request

Use a focused pull request against `ansible/aap-skills:main`.

Include:

- What changed and why.
- Skills, references, or validation behavior affected.
- MCP tools and external sources required, if applicable.
- Read-only, write, or destructive risk classification.
- Validation commands and results.
- Live-environment limitations or checks not run.

Keep generated files and unrelated local reports out of the pull request. Respond to review comments with follow-up commits; do not rewrite shared history or force-push unless a maintainer requests it.

## Content and licensing

Write clear, inclusive, task-focused documentation. Follow the [Contributor Covenant](https://www.contributor-covenant.org/) standards for respectful collaboration.

Contributions are licensed under Apache License 2.0 as described in [LICENSE](LICENSE).
