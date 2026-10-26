"""Tests for scripts/validate_skills.py.

Focused on the SEP-2640 per-skill limits and on skill identity — the directory
name, the front matter `name`, and the `id` must all agree, because the final
segment of the URI the MCP server derives is the directory name and SEP-2640
makes a mismatch a load failure on a conforming host.
"""

from pathlib import Path

import validate_skills

SKILL_MD_TEMPLATE = """---
name: {name}
description: |
  Example skill used by the validator test suite.

  Use when: exercising validate_skills.py.

  NOT for: real platform operations.
license: Apache-2.0
id: {skill_id}
version: 1.0.0
category: testing
mcpToolDependencies: []
supportBoundary:
  model: validated
---

# Example

Body text.
"""


def make_skill(parent: Path, name: str = 'aap-example', dirname: str = None,
               skill_id: str = None) -> Path:
    """Create a minimal skill that passes validation unless told otherwise."""
    skill_dir = parent / (dirname or name)
    skill_dir.mkdir(parents=True)
    (skill_dir / 'SKILL.md').write_text(
        SKILL_MD_TEMPLATE.format(name=name, skill_id=skill_id or name),
        encoding='utf-8')
    return skill_dir


def add_files(skill_dir: Path, count: int) -> None:
    """Add `count` empty files, so only the resource count moves."""
    filler = skill_dir / 'filler'
    filler.mkdir(exist_ok=True)
    for i in range(count):
        (filler / f'file-{i:04d}.md').touch()


def pad_to(skill_dir: Path, total_bytes: int) -> None:
    """Add one sparse file bringing the skill's total size to `total_bytes`."""
    current = sum(f.stat().st_size
                  for f in validate_skills.collect_skill_files(skill_dir))
    with (skill_dir / 'padding.bin').open('wb') as f:
        f.truncate(total_bytes - current)


def messages(errors):
    return [e.message for e in errors]


def errors_only(errors):
    return [e for e in errors if e.severity == 'error']


# --- Resource count limit (512 entries) ------------------------------------

def test_resource_count_at_the_limit_passes(tmp_path):
    skill_dir = make_skill(tmp_path)
    add_files(skill_dir, validate_skills.MAX_RESOURCES_PER_SKILL - 1)

    assert len(validate_skills.collect_skill_files(skill_dir)) == 512
    assert validate_skills.validate_skill_limits(skill_dir) == []


def test_resource_count_one_over_the_limit_fails(tmp_path):
    skill_dir = make_skill(tmp_path)
    add_files(skill_dir, validate_skills.MAX_RESOURCES_PER_SKILL)

    errors = validate_skills.validate_skill_limits(skill_dir)

    assert len(errors) == 1
    assert '513 files' in errors[0].message
    assert 'limit 512' in errors[0].message


def test_resource_count_error_names_the_skill(tmp_path):
    skill_dir = make_skill(tmp_path, name='aap-oversized')
    add_files(skill_dir, validate_skills.MAX_RESOURCES_PER_SKILL)

    assert 'aap-oversized' in str(
        validate_skills.validate_skill_limits(skill_dir)[0])


# --- Total size limit (16 MiB) ---------------------------------------------

def test_total_size_at_the_limit_passes(tmp_path):
    skill_dir = make_skill(tmp_path)
    pad_to(skill_dir, validate_skills.MAX_SKILL_BYTES)

    assert validate_skills.validate_skill_limits(skill_dir) == []


def test_total_size_one_over_the_limit_fails(tmp_path):
    skill_dir = make_skill(tmp_path)
    pad_to(skill_dir, validate_skills.MAX_SKILL_BYTES + 1)

    errors = validate_skills.validate_skill_limits(skill_dir)

    assert len(errors) == 1
    assert '16,777,217 bytes' in errors[0].message
    assert 'limit 16,777,216 bytes' in errors[0].message


def test_total_size_error_names_the_skill(tmp_path):
    skill_dir = make_skill(tmp_path, name='aap-oversized')
    pad_to(skill_dir, validate_skills.MAX_SKILL_BYTES + 1)

    assert 'aap-oversized' in str(
        validate_skills.validate_skill_limits(skill_dir)[0])


def test_limits_match_the_values_sep_2640_fixes():
    assert validate_skills.MAX_RESOURCES_PER_SKILL == 512
    assert validate_skills.MAX_SKILL_BYTES == 16_777_216


# --- What counts as a resource ---------------------------------------------

def test_collect_includes_skill_md_and_every_nested_file(tmp_path):
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'a.md').write_text('a', encoding='utf-8')
    (skill_dir / 'scripts').mkdir()
    (skill_dir / 'scripts' / 'run.py').write_text('x', encoding='utf-8')

    found = [p.relative_to(skill_dir).as_posix()
             for p in validate_skills.collect_skill_files(skill_dir)]

    assert found == ['SKILL.md', 'references/a.md', 'scripts/run.py']


def test_collect_does_not_follow_symlinked_directories(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'secret.md').write_text('x', encoding='utf-8')
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'link').symlink_to(outside, target_is_directory=True)

    found = [p.relative_to(skill_dir).as_posix()
             for p in validate_skills.collect_skill_files(skill_dir)]

    assert found == ['SKILL.md']


def test_unreadable_file_is_reported_rather_than_crashing(tmp_path):
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'broken.md').symlink_to(tmp_path / 'does-not-exist')

    messages_ = messages(validate_skills.validate_skill_limits(skill_dir))

    assert any('Cannot determine the size of broken.md' in m
               for m in messages_)


# --- Identity ---------------------------------------------------------------

def test_valid_skill_has_no_errors(tmp_path):
    assert validate_skills.validate_skill(make_skill(tmp_path)) == []


def test_directory_name_must_match_front_matter_name(tmp_path):
    skill_dir = make_skill(tmp_path, name='aap-example', dirname='aap-renamed')

    assert any("Directory name 'aap-renamed' does not match name field "
               "'aap-example'" in m
               for m in messages(validate_skills.validate_skill(skill_dir)))


def test_id_must_match_front_matter_name(tmp_path):
    skill_dir = make_skill(tmp_path, name='aap-example',
                           skill_id='aap-something-else')

    assert any("id 'aap-something-else' must match name 'aap-example'" in m
               for m in messages(validate_skills.validate_skill(skill_dir)))


def test_directory_without_the_aap_prefix_fails(tmp_path):
    skill_dir = make_skill(tmp_path, name='example', dirname='example')

    assert any("Directory name 'example' must start with 'aap-'" in m
               for m in messages(validate_skills.validate_skill(skill_dir)))


# --- Front matter the server's reader will not parse ------------------------

def write_frontmatter(tmp_path: Path, yaml_text: str) -> Path:
    skill_dir = tmp_path / 'aap-example'
    skill_dir.mkdir()
    skill_md = skill_dir / 'SKILL.md'
    skill_md.write_text(f"---\n{yaml_text}---\n\n# Example\n", encoding='utf-8')
    return skill_md


def test_multi_line_flow_sequence_is_rejected(tmp_path):
    """The real aap-platform-health-check defect: valid YAML, unservable."""
    skill_md = write_frontmatter(tmp_path, """name: aap-example
mcpToolDependencies:
  - server: aap
    tools: [
            # system_monitoring
            status_retrieve, me_list]
""")

    errors = validate_skills.validate_frontmatter_subset(skill_md)

    assert len(errors) == 1
    assert 'line 5' in errors[0].message
    assert 'open and close on the same line' in errors[0].message


def test_multi_line_flow_mapping_is_rejected(tmp_path):
    skill_md = write_frontmatter(tmp_path, """name: aap-example
supportBoundary: {
  model: red-hat }
""")

    errors = validate_skills.validate_frontmatter_subset(skill_md)

    assert len(errors) == 1
    assert 'line 3' in errors[0].message


def test_one_line_flow_collections_are_accepted(tmp_path):
    """The reader supports these, and real skills use them for empty lists."""
    skill_md = write_frontmatter(tmp_path, """name: aap-example
mcpToolDependencies: []
supportBoundary: {model: red-hat}
tools: [status_retrieve, me_list]
""")

    assert validate_skills.validate_frontmatter_subset(skill_md) == []


def test_block_sequences_are_accepted(tmp_path):
    skill_md = write_frontmatter(tmp_path, """name: aap-example
mcpToolDependencies:
  - server: aap
    tools:
      # system_monitoring
      - status_retrieve
      - me_list
""")

    assert validate_skills.validate_frontmatter_subset(skill_md) == []


def test_multi_line_quoted_value_is_rejected(tmp_path):
    skill_md = write_frontmatter(tmp_path, """name: aap-example
compatibility: "Requires the AAP MCP Server
  for Ansible Automation Platform 2.5+"
""")

    errors = validate_skills.validate_frontmatter_subset(skill_md)

    assert len(errors) == 1
    assert 'must close on the same line' in errors[0].message


def test_block_scalars_are_accepted(tmp_path):
    """Block scalars are in the subset, and are how multi-line text is written."""
    skill_md = write_frontmatter(tmp_path, """name: aap-example
description: |
  Determine what access a user has.

  Use when: reviewing access.

  NOT for: auditing.
allowed-tools: >-
  status_retrieve me_list
  users_list
""")

    assert validate_skills.validate_frontmatter_subset(skill_md) == []


def test_anchors_and_aliases_are_rejected(tmp_path):
    skill_md = write_frontmatter(tmp_path, """name: aap-example
base: &base
  model: red-hat
supportBoundary: *base
""")

    messages_ = messages(validate_skills.validate_frontmatter_subset(skill_md))

    assert messages_
    assert all('anchors, aliases and tags' in m for m in messages_)


def test_subset_check_runs_as_part_of_validate_skill(tmp_path):
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'SKILL.md').write_text(
        "---\nname: aap-example\ntools: [\n  a, b]\n---\n\n# Example\n",
        encoding='utf-8')

    assert any('open and close on the same line' in m
               for m in messages(validate_skills.validate_skill(skill_dir)))


def test_pyyaml_accepts_what_the_server_rejects(tmp_path):
    """Why this check exists: PyYAML alone would have passed the defect."""
    import yaml

    skill_md = write_frontmatter(tmp_path, """name: aap-example
tools: [
  status_retrieve, me_list]
""")
    frontmatter, _ = validate_skills.split_frontmatter(
        skill_md.read_text(encoding='utf-8'))

    assert yaml.safe_load(frontmatter)['tools'] == ['status_retrieve', 'me_list']
    assert validate_skills.validate_frontmatter_subset(skill_md) != []


# --- Supporting-file references ---------------------------------------------

def body(skill_dir: Path, markdown: str) -> None:
    """Append body text to a skill's SKILL.md."""
    skill_md = skill_dir / 'SKILL.md'
    skill_md.write_text(skill_md.read_text(encoding='utf-8') + markdown,
                        encoding='utf-8')


def test_path_escaping_the_skill_directory_is_rejected(tmp_path):
    """The original defect: content at the repository root is never served."""
    skill_dir = make_skill(tmp_path)
    body(skill_dir, 'Follow `../../context/output-format.md` for reports.\n')

    errors = validate_skills.validate_skill_references(skill_dir)

    assert len(errors) == 1
    assert 'leaves the skill directory' in errors[0].message
    assert 'SKILL.md:' in errors[0].message


def test_markdown_link_to_a_local_file_is_rejected(tmp_path):
    """A relative href is meaningless to a client reading over MCP."""
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'baselines.md').write_text('x',
                                                           encoding='utf-8')
    body(skill_dir, 'Follow [baselines](references/baselines.md).\n')

    errors = validate_skills.validate_skill_references(skill_dir)

    assert len(errors) == 1
    assert 'Markdown link to the local path' in errors[0].message


def test_markdown_link_to_a_url_or_anchor_is_accepted(tmp_path):
    skill_dir = make_skill(tmp_path)
    body(skill_dir, '[SEP-2640](https://modelcontextprotocol.io/seps/2640)\n'
                    '[a section](#description)\n'
                    '[mail](mailto:someone@example.com)\n')

    assert validate_skills.validate_skill_references(skill_dir) == []


def test_backticked_path_from_the_skill_root_is_accepted(tmp_path):
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'baselines.md').write_text('x',
                                                           encoding='utf-8')
    body(skill_dir, 'Read `references/baselines.md` for thresholds.\n'
                    'The front matter lives in `SKILL.md`.\n')

    assert validate_skills.validate_skill_references(skill_dir) == []


def test_path_into_a_skill_subdirectory_must_exist(tmp_path):
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'baselines.md').write_text('x',
                                                           encoding='utf-8')
    body(skill_dir, 'Read `references/typo.md` for thresholds.\n')

    errors = validate_skills.validate_skill_references(skill_dir)

    assert len(errors) == 1
    assert "'references/typo.md' is not a file of this skill" \
        in errors[0].message


def test_an_example_path_in_prose_is_not_treated_as_a_citation(tmp_path):
    """No 'reports/' directory, so this is prose, not a reference."""
    skill_dir = make_skill(tmp_path)
    body(skill_dir, 'Save as `reports/health-check_2026-04-12.md`.\n')

    assert validate_skills.validate_skill_references(skill_dir) == []


def test_sibling_reference_inside_references_is_rejected(tmp_path):
    """Paths resolve from the skill root, not from the file citing them."""
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'baselines.md').write_text('x',
                                                           encoding='utf-8')
    (skill_dir / 'references' / 'sources.md').write_text(
        'These override `baselines.md`.\n', encoding='utf-8')

    errors = validate_skills.validate_skill_references(skill_dir)

    assert len(errors) == 1
    assert 'references/sources.md:1' in errors[0].message
    assert "Write 'references/baselines.md'" in errors[0].message


def test_synced_context_copies_are_not_held_to_the_citation_rules(tmp_path):
    """scripts/sync_shared.py owns context/; it is validated at its source."""
    skill_dir = make_skill(tmp_path)
    (skill_dir / 'context').mkdir()
    (skill_dir / 'context' / 'output-format.md').write_text(
        'Save as `reports/example.md`. See [schema](./schema/x.json).\n',
        encoding='utf-8')

    assert validate_skills.validate_skill_references(skill_dir) == []


def test_reference_check_runs_as_part_of_validate_skill(tmp_path):
    skill_dir = make_skill(tmp_path)
    body(skill_dir, 'Follow `../../context/output-format.md`.\n')

    assert any('leaves the skill directory' in m
               for m in messages(validate_skills.validate_skill(skill_dir)))


# --- Discovery --------------------------------------------------------------

def test_discovery_finds_a_skill_whose_directory_lost_the_prefix(tmp_path):
    """A misnamed skill must be found, or the naming checks never fire."""
    skills_dir = tmp_path / 'skills'
    skills_dir.mkdir()
    make_skill(skills_dir, name='aap-example')
    make_skill(skills_dir, name='example', dirname='example')
    (skills_dir / 'not-a-skill').mkdir()

    found = validate_skills.discover_skill_dirs(skills_dir)

    assert [d.name for d in found] == ['aap-example', 'example']


# --- Ordering ---------------------------------------------------------------

def test_limits_are_reported_even_when_front_matter_is_unparseable(tmp_path):
    skill_dir = tmp_path / 'aap-example'
    skill_dir.mkdir()
    (skill_dir / 'SKILL.md').write_text('no front matter\n', encoding='utf-8')
    add_files(skill_dir, validate_skills.MAX_RESOURCES_PER_SKILL)

    messages_ = messages(validate_skills.validate_skill(skill_dir))

    assert any('resource limit' in m for m in messages_)
    assert any('front matter' in m for m in messages_)


# --- The skills this repository actually publishes --------------------------

def test_published_skills_pass_validation():
    repo_root = Path(__file__).resolve().parent.parent
    skill_dirs = validate_skills.discover_skill_dirs(repo_root / 'skills')

    assert skill_dirs, 'no skills found under skills/'
    for skill_dir in skill_dirs:
        errors = errors_only(validate_skills.validate_skill(skill_dir))
        assert errors == [], f"{skill_dir.name}: {messages(errors)}"
