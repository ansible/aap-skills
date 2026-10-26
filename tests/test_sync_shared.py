"""Tests for scripts/sync_shared.py.

Shared content has to be duplicated into every skill that uses it, because a
file outside a skill directory is not served over MCP at all. These tests
cover the part that makes the duplication safe: a skill opts in by having the
destination file, the copy is generated from a single source, and --check
fails when the two have drifted.
"""

from pathlib import Path

import sync_shared

SKILL_MD = """---
name: aap-example
description: |
  Example skill.

  Use when: exercising sync_shared.py.

  NOT for: real platform operations.
license: Apache-2.0
---

# Example
"""

SHARED = """---
name: output-format
description: Shared standard.
---

# Output format
"""


def make_repo(tmp_path: Path, *, opt_in: bool) -> Path:
    """A repository with one shared source and one skill."""
    (tmp_path / 'context').mkdir()
    (tmp_path / 'context' / 'output-format.md').write_text(SHARED,
                                                           encoding='utf-8')
    skill_dir = tmp_path / 'skills' / 'aap-example'
    skill_dir.mkdir(parents=True)
    (skill_dir / 'SKILL.md').write_text(SKILL_MD, encoding='utf-8')
    if opt_in:
        (skill_dir / 'context').mkdir()
        (skill_dir / 'context' / 'output-format.md').touch()
    return tmp_path


def sync(root: Path, monkeypatch, check=False) -> int:
    monkeypatch.setattr(sync_shared, 'repo_root', lambda: root)
    monkeypatch.setattr('sys.argv',
                        ['sync_shared.py'] + (['--check'] if check else []))
    return sync_shared.main()


def copy_of(root: Path) -> Path:
    return root / 'skills' / 'aap-example' / 'context' / 'output-format.md'


def test_a_skill_opts_in_by_having_the_destination_file(tmp_path,
                                                        monkeypatch):
    root = make_repo(tmp_path, opt_in=True)

    assert sync(root, monkeypatch) == 0
    assert '# Output format' in copy_of(root).read_text(encoding='utf-8')


def test_a_skill_without_the_file_is_left_alone(tmp_path, monkeypatch):
    root = make_repo(tmp_path, opt_in=False)

    assert sync(root, monkeypatch) == 0
    assert not copy_of(root).exists()


def test_the_copy_carries_a_do_not_edit_banner_after_the_front_matter(
        tmp_path, monkeypatch):
    """The banner must not displace front matter from line 1."""
    root = make_repo(tmp_path, opt_in=True)
    sync(root, monkeypatch)

    lines = copy_of(root).read_text(encoding='utf-8').splitlines()

    assert lines[0] == '---'
    assert lines[3] == '---'
    assert 'Do not edit' in lines[4]
    assert 'context/output-format.md' in lines[4]


def test_check_passes_when_the_copy_is_current(tmp_path, monkeypatch):
    root = make_repo(tmp_path, opt_in=True)
    sync(root, monkeypatch)

    assert sync(root, monkeypatch, check=True) == 0


def test_check_fails_when_the_copy_has_drifted(tmp_path, monkeypatch):
    root = make_repo(tmp_path, opt_in=True)
    sync(root, monkeypatch)
    copy_of(root).write_text('edited by hand\n', encoding='utf-8')

    assert sync(root, monkeypatch, check=True) == 1


def test_check_fails_when_the_source_changed(tmp_path, monkeypatch):
    root = make_repo(tmp_path, opt_in=True)
    sync(root, monkeypatch)
    (root / 'context' / 'output-format.md').write_text(
        SHARED + '\nA new rule.\n', encoding='utf-8')

    assert sync(root, monkeypatch, check=True) == 1
    assert sync(root, monkeypatch) == 0
    assert sync(root, monkeypatch, check=True) == 0


def test_check_does_not_write(tmp_path, monkeypatch):
    root = make_repo(tmp_path, opt_in=True)

    assert sync(root, monkeypatch, check=True) == 1
    assert copy_of(root).read_text(encoding='utf-8') == ''


def test_the_published_copies_are_in_sync(monkeypatch):
    root = Path(__file__).resolve().parent.parent
    monkeypatch.setattr('sys.argv', ['sync_shared.py', '--check'])

    assert sync_shared.main() == 0
    assert sync_shared.planned_copies(root), 'no skill opted in to shared content'
