# Contributing to AAP Skills

Thank you for contributing to AAP Skills for Ansible Automation Platform.

## Before you start

- Read the [README](README.md) and [Ansible Skill Content Type Definition](docs/content-type-definition.md).
- Keep changes scoped to this repository. Do not add credentials, tokens, customer data, or environment-specific secrets.
- Use the AAP MCP Server as the integration point for platform operations. Skills do not call AAP APIs directly, use the `awx` CLI, or connect through SSH.

## Create a change

1. Fork `ansible/aap-skills` and create a focused feature branch from `main`.
2. Add or update content under the appropriate repository path.
3. Keep each skill in `skills/aap-<kebab-case-name>/SKILL.md`. The directory name, the frontmatter `name`, and the frontmatter `id` must all match. The MCP server derives the final segment of a skill's `skill://` URI from the directory name, and SEP-2640 makes a mismatch between that segment and the frontmatter `name` a load failure on a conforming host.
4. For an AAP platform skill, follow the three-layer frontmatter defined in the content type specification:
   - agentskills.io base fields, including `name`, `description`, and `license`.
   - Red Hat skill fields, including `id`, `version`, `category`, `mcpToolDependencies`, and `supportBoundary`.
   - AAP operational fields, including `riskLevel` and `aapVersion`.
5. Declare every MCP tool used by the skill in `mcpToolDependencies`. Keep `allowed-tools` consistent when it is present.
6. Default platform operations to read-only. Write or destructive workflows need explicit user confirmation, clear impact details, and RBAC enforcement.
7. Put substantial, version-sensitive material in a skill `references/` directory. Keep links relative and verify them locally.
8. For report-generating skills, follow [`context/output-format.md`](context/output-format.md), including the MCP quick reference and standard footer.

## Per-skill limits

Every file in a skill directory is served as an individual MCP resource, and [SEP-2640](https://modelcontextprotocol.io/seps/2640-skills-extension) fixes two limits on that set:

| Limit | Value | Counted over |
|-------|-------|--------------|
| Resources per skill | 512 entries | Every file in the skill directory, `SKILL.md` included |
| Total size per skill | 16 MiB (16,777,216 bytes) | The sum of those files' byte sizes |

A conforming host is only required to load skills up to these values, so a skill over either one may simply refuse to load. `make validate` rejects it before it reaches a release.

## Front matter style

Write front matter in block style. Use `- item` on its own line for lists, and a block scalar (`|` or `>-`) for text spanning lines.

This is narrower than YAML allows, and deliberately so. The MCP server does not read `SKILL.md` with a general YAML parser — it uses a restricted reader covering the subset skills actually use, and it throws on anything outside that subset rather than risk reading a construct differently from a full parser. SEP-2640 makes that agreement load-bearing: a host re-parses the same bytes and compares the result field by field against the server's, and any discrepancy is a load failure.

So valid YAML can still be unservable, and the failure is silent — a skill the server cannot read is skipped from the catalog entirely, not degraded. `make validate` rejects the constructs most likely to appear in hand-written front matter:

| Not supported | Write instead |
|---------------|---------------|
| A flow collection spanning lines — `tools: [` with items below | A block sequence, `- item` per line |
| A quoted value spanning lines | A block scalar, `\|` or `>-` |
| Anchors, aliases and tags — `&base`, `*base`, `!tag` | Repeat the value |

One-line flow collections are fine: `mcpToolDependencies: []` and `tools: [a, b]` both read correctly.

## Validate locally

The repository uses Python 3.11 or newer and `uv` for development dependencies.

```bash
make install
make validate
```

`make validate` runs the skill validator, codespell, and the validator's own unit tests. To run a single part:

```bash
make validate-spelling   # codespell only
make test                # validator unit tests only
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
