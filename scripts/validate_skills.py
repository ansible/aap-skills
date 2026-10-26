#!/usr/bin/env python3
"""
Validate AAP skills against the content type definition.

Checks:
- Directory structure (skills/aap-{name}/SKILL.md)
- YAML front matter parsing
- Required fields (agentskills.io + Red Hat Skill fields)
- Field constraints (kebab-case, semver, etc.)
- Description structure (Use when, NOT for)
- SEP-2640 per-skill resource count and total size limits
- Supporting-file references resolve inside the skill, from the skill root
- Internal links
"""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

# ANSI colors for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Required fields from content type definition
REQUIRED_BASE_FIELDS = ['name', 'description', 'license']
REQUIRED_RH_FIELDS = ['id', 'version', 'category', 'mcpToolDependencies', 'supportBoundary']

# Valid SPDX license identifiers (common subset)
VALID_LICENSES = ['Apache-2.0', 'MIT', 'GPL-3.0', 'BSD-3-Clause', 'ISC']

# Per-skill limits fixed by SEP-2640. Hosts must support skills up to these
# values; servers should not serve a skill that exceeds either one. A skill
# over the limit is content that is not guaranteed to load on any conforming
# host, so it is rejected here rather than published.
MAX_RESOURCES_PER_SKILL = 512
MAX_SKILL_BYTES = 16 * 1024 * 1024  # 16 MiB (16,777,216 bytes)

# Every skill directory must carry the AAP prefix.
SKILL_DIR_PREFIX = 'aap-'

# Front matter starts on line 2 of SKILL.md, after the opening '---'.
FRONTMATTER_FIRST_LINE = 2

# Content a skill writes itself, and so is responsible for citing correctly.
# 'context/' is excluded: scripts/sync_shared.py owns it, the copies there are
# validated at their source, and they are also read by people browsing the
# repository, so their prose is not written to this convention.
AUTHORED_DIRS = ('references',)

# A Markdown link, capturing its target.
MARKDOWN_LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')

# A target that does not name a file in the repository: an absolute URI
# ('https:', 'mailto:') or a same-document anchor.
NON_LOCAL_TARGET = re.compile(r'^(?:[a-z][a-z\d+.-]*:|#)', re.IGNORECASE)

# A backticked token that cites a Markdown file this skill ships. The leading
# '/' and './' or '../' runs are matched so that a path out of the skill is
# caught rather than silently skipped as unrecognised prose.
CITED_MARKDOWN = re.compile(r'`(/?(?:\.{1,2}/)*[\w][\w./-]*\.md)`')


class ValidationError:
    def __init__(self, skill_path: Path, message: str, severity: str = 'error'):
        self.skill_path = skill_path
        self.message = message
        self.severity = severity

    def __str__(self):
        color = RED if self.severity == 'error' else YELLOW
        symbol = '✗' if self.severity == 'error' else '⚠'
        return f"{color}{symbol} {self.skill_path.parent.name}: {self.message}{RESET}"


def split_frontmatter(content: str) -> Tuple[str, str]:
    """Split SKILL.md into its front matter YAML and its body.

    Returns ('', '') when the delimiters are missing. The front matter begins
    on line 2 of the file, which is what FRONTMATTER_FIRST_LINE records.
    """
    if not content.startswith('---\n'):
        return '', ''
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return '', ''
    return parts[1], parts[2]


def parse_skill_frontmatter(skill_md: Path) -> Tuple[Dict[str, Any], str, List[ValidationError]]:
    """Parse SKILL.md and extract front matter and body."""
    errors = []

    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        errors.append(ValidationError(skill_md, f"Failed to read file: {e}"))
        return {}, "", errors

    # Extract front matter
    if not content.startswith('---\n'):
        errors.append(ValidationError(skill_md, "Missing front matter delimiter (---) at start of file"))
        return {}, "", errors

    frontmatter_str, body = split_frontmatter(content)
    if not frontmatter_str and not body:
        errors.append(ValidationError(skill_md, "Missing closing front matter delimiter (----)"))
        return {}, "", errors

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
        if not isinstance(frontmatter, dict):
            errors.append(ValidationError(skill_md, "Front matter must be a YAML dictionary"))
            return {}, body, errors
    except yaml.YAMLError as e:
        errors.append(ValidationError(skill_md, f"Invalid YAML in front matter: {e}"))
        return {}, body, errors

    return frontmatter, body, errors


def validate_kebab_case(value: str) -> bool:
    """Validate kebab-case: lowercase letters, numbers, hyphens; no consecutive hyphens."""
    if not value:
        return False
    if not 1 <= len(value) <= 64:
        return False
    if not re.match(r'^[a-z0-9-]+$', value):
        return False
    if '--' in value:
        return False
    if value.startswith('-') or value.endswith('-'):
        return False
    return True


def validate_semver(value: str) -> bool:
    """Validate semantic versioning (X.Y.Z)."""
    return bool(re.match(r'^\d+\.\d+\.\d+$', value))


def validate_frontmatter_subset(skill_md: Path) -> List[ValidationError]:
    """Reject front matter the MCP server's own reader will not parse.

    The server does not use PyYAML. It reads SKILL.md with a restricted YAML
    reader that covers the subset real skills use and throws on anything else,
    rather than risk reading a construct differently from a full YAML parser.
    That strictness is load-bearing rather than fussy: SEP-2640 makes a host
    re-parse the same bytes and compare the result field by field against the
    server's, and any discrepancy is a load failure, so the two parsers have to
    agree. The subset is their intersection.

    The practical consequence is that valid YAML 1.2 can still be unservable.
    A skill the server cannot read is skipped from the catalog entirely — not
    degraded, absent — so this has to fail here rather than at startup.

    These are the constructs that are both outside the subset and plausible in
    hand-written front matter. The authoritative check is the server's reader;
    this one is the fast feedback at PR time.
    """
    errors = []

    try:
        content = skill_md.read_text(encoding='utf-8')
    except OSError:
        return errors  # reported by parse_skill_frontmatter

    frontmatter_str, _ = split_frontmatter(content)
    if not frontmatter_str:
        return errors

    try:
        tokens = list(yaml.scan(frontmatter_str))
    except yaml.YAMLError:
        return errors  # invalid YAML outright, reported by the parser

    def at(mark) -> int:
        return mark.line + FRONTMATTER_FIRST_LINE

    flow_starts = []
    for token in tokens:
        kind = type(token).__name__

        if kind in ('FlowSequenceStartToken', 'FlowMappingStartToken'):
            flow_starts.append(token)
        elif kind in ('FlowSequenceEndToken', 'FlowMappingEndToken'):
            if not flow_starts:
                continue
            start = flow_starts.pop()
            if start.start_mark.line != token.end_mark.line:
                bracket = '[' if kind == 'FlowSequenceEndToken' else '{'
                errors.append(ValidationError(
                    skill_md,
                    f"line {at(start.start_mark)}: a flow collection '{bracket}' "
                    f"must open and close on the same line. The server's front "
                    f"matter reader rejects a multi-line flow collection and "
                    f"skips the whole skill. Use a block sequence "
                    f"('- item' on its own line) instead."))
        elif kind in ('AnchorToken', 'AliasToken', 'TagToken'):
            errors.append(ValidationError(
                skill_md,
                f"line {at(token.start_mark)}: anchors, aliases and tags are "
                f"not supported by the server's front matter reader."))
        elif kind == 'ScalarToken' and token.style in ('"', "'"):
            if token.start_mark.line != token.end_mark.line:
                errors.append(ValidationError(
                    skill_md,
                    f"line {at(token.start_mark)}: a quoted value must close "
                    f"on the same line. The server's front matter reader "
                    f"rejects a multi-line quoted value. Use a block scalar "
                    f"('|' or '>') for text spanning lines."))

    return errors


def authored_markdown(skill_dir: Path) -> List[Path]:
    """SKILL.md and the Markdown the skill itself wrote, in a stable order."""
    files = [skill_dir / 'SKILL.md']
    for name in AUTHORED_DIRS:
        files.extend(sorted((skill_dir / name).rglob('*.md')))
    return [f for f in files if f.is_file()]


def validate_skill_references(skill_dir: Path) -> List[ValidationError]:
    """Check that every supporting file a skill cites can actually be read.

    Two rules, and they are independent — a reference has to satisfy both.

    Location. A skill is served as a closed set of files. The MCP server
    builds its catalog from the skill's own directory and SEP-2640 rejects an
    entry listing a resource outside it, so a path that escapes the directory
    has no URI at all. Symlinking out is not a way around this: the SDK's
    filesystem adapter reports a symlink as unsupported and drops the whole
    skill. Shared content must be copied in, which scripts/sync_shared.py
    does.

    Style. A client reads a file as `read(skill, ref)`, where `ref` is a path
    relative to the skill's root. That resolution is against the root, not
    against the file doing the citing, so a reference in references/x.md to a
    sibling must still be written 'references/y.md'. A relative Markdown link
    is worse than useless here: its target means nothing over MCP, and a
    label that disagrees with it is exactly what makes a client construct a
    URI of its own and miss.

    A full 'skill://...' URI is not the answer either. The authority segment
    comes from the server's deployment-time prefix, not from the skill, so a
    URI written into content is wrong on any server configured differently.
    """
    errors = []

    for md_file in authored_markdown(skill_dir):
        where = md_file.relative_to(skill_dir).as_posix()
        try:
            lines = md_file.read_text(encoding='utf-8').splitlines()
        except OSError:
            continue  # reported by validate_skill_limits

        for number, line in enumerate(lines, 1):
            for target in MARKDOWN_LINK.findall(line):
                if NON_LOCAL_TARGET.match(target):
                    continue
                errors.append(ValidationError(
                    skill_dir / 'SKILL.md',
                    f"{where}:{number}: Markdown link to the local path "
                    f"'{target}'. A relative link does not resolve for a "
                    f"client reading this skill over MCP. Cite the path "
                    f"relative to the skill root in backticks instead."))

            for cited in CITED_MARKDOWN.findall(line):
                errors.extend(check_citation(skill_dir, where, number, cited))

    return errors


def check_citation(skill_dir: Path, where: str, number: int,
                   cited: str) -> List[ValidationError]:
    """Check one backticked Markdown path cited from inside a skill."""
    skill_md = skill_dir / 'SKILL.md'
    location = f"{where}:{number}"

    if cited.startswith('/') or '..' in Path(cited).parts:
        return [ValidationError(
            skill_md,
            f"{location}: '{cited}' leaves the skill directory. Nothing "
            f"outside it is served over MCP, so no URI reaches that file. "
            f"Copy the content into the skill — see "
            f"scripts/sync_shared.py — and cite it from the skill root.")]

    first = Path(cited).parts[0]
    if first != cited:
        # A path into one of the skill's own subdirectories must land on a
        # file. Anything else is prose, such as an example report name.
        if (skill_dir / first).is_dir() and not (skill_dir / cited).is_file():
            return [ValidationError(
                skill_md,
                f"{location}: '{cited}' is not a file of this skill.")]
        return []

    if cited == 'SKILL.md':
        return []

    # A bare file name resolves against the skill root, not against the file
    # citing it, so a sibling reference inside references/ silently misses.
    matches = sorted(p.relative_to(skill_dir).as_posix()
                     for p in skill_dir.rglob(cited) if p.is_file())
    if matches and cited not in matches:
        return [ValidationError(
            skill_md,
            f"{location}: '{cited}' resolves from the skill root, not from "
            f"the file citing it, so it reaches nothing. Write "
            f"'{matches[0]}'.")]

    return []


def collect_skill_files(skill_dir: Path) -> List[Path]:
    """Every file the MCP server exposes as a resource for this skill.

    SEP-2640 requires a skill's resource listing to be complete — every file in
    the skill directory, SKILL.md included — so the per-skill limits are counted
    over exactly this set. Symlinked directories are not followed: the server
    does not serve outside the skill directory either, and following them here
    would count files it will never expose.
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(skill_dir, followlinks=False):
        dirnames.sort()
        for filename in sorted(filenames):
            files.append(Path(dirpath) / filename)
    return files


def validate_skill_limits(skill_dir: Path) -> List[ValidationError]:
    """Check a skill against the SEP-2640 per-skill resource and size limits."""
    errors = []
    skill_md = skill_dir / 'SKILL.md'
    files = collect_skill_files(skill_dir)

    if len(files) > MAX_RESOURCES_PER_SKILL:
        errors.append(ValidationError(
            skill_md,
            f"Exceeds the SEP-2640 resource limit: {len(files)} files, "
            f"limit {MAX_RESOURCES_PER_SKILL}. Every file in the skill "
            f"directory is exposed as a resource, SKILL.md included."))

    total_bytes = 0
    for skill_file in files:
        try:
            total_bytes += skill_file.stat().st_size
        except OSError as e:
            errors.append(ValidationError(
                skill_md,
                f"Cannot determine the size of "
                f"{skill_file.relative_to(skill_dir)}: {e}"))

    if total_bytes > MAX_SKILL_BYTES:
        errors.append(ValidationError(
            skill_md,
            f"Exceeds the SEP-2640 total size limit: {total_bytes:,} bytes "
            f"across {len(files)} file(s), limit {MAX_SKILL_BYTES:,} bytes "
            f"(16 MiB)."))

    return errors


def validate_skill(skill_dir: Path) -> List[ValidationError]:
    """Validate a single skill directory."""
    errors = []
    skill_md = skill_dir / 'SKILL.md'

    # Check SKILL.md exists
    if not skill_md.exists():
        errors.append(ValidationError(skill_md, "SKILL.md not found"))
        return errors

    # Directory naming convention. Checked here rather than at discovery so a
    # misnamed skill is reported instead of silently skipped.
    if not skill_dir.name.startswith(SKILL_DIR_PREFIX):
        errors.append(ValidationError(
            skill_md,
            f"Directory name '{skill_dir.name}' must start with "
            f"'{SKILL_DIR_PREFIX}'"))

    # SEP-2640 per-skill limits. Independent of front matter, so they run before
    # parsing and are not short-circuited by a parse failure.
    errors.extend(validate_skill_limits(skill_dir))

    # Front matter the server's reader will not parse. Checked on the raw text
    # before PyYAML gets it, because PyYAML is the more permissive of the two
    # and accepts constructs that leave the skill unservable.
    errors.extend(validate_frontmatter_subset(skill_md))

    # Supporting files the skill points a client at. Also independent of front
    # matter, and the failure it catches is silent at runtime: the client gets
    # a resource-not-found for a file that was never servable.
    errors.extend(validate_skill_references(skill_dir))

    # Parse front matter
    frontmatter, _body, parse_errors = parse_skill_frontmatter(skill_md)
    errors.extend(parse_errors)
    if parse_errors:
        return errors  # Can't continue validation without valid front matter

    # Validate required base fields (agentskills.io)
    for field in REQUIRED_BASE_FIELDS:
        if field not in frontmatter:
            errors.append(ValidationError(skill_md, f"Missing required field: {field}"))

    # Validate required Red Hat Skill fields
    for field in REQUIRED_RH_FIELDS:
        if field not in frontmatter:
            errors.append(ValidationError(skill_md, f"Missing required Red Hat Skill field: {field}"))

    # Validate 'name' field
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not validate_kebab_case(name):
            errors.append(ValidationError(skill_md, f"Invalid name '{name}': must be kebab-case, 1-64 chars, no consecutive hyphens"))

        # Name must match directory name (name already includes 'aap-' prefix)
        if skill_dir.name != name:
            errors.append(ValidationError(skill_md, f"Directory name '{skill_dir.name}' does not match name field '{name}'"))

    # Validate 'id' matches 'name'
    if 'id' in frontmatter and 'name' in frontmatter:
        if frontmatter['id'] != frontmatter['name']:
            errors.append(ValidationError(skill_md, f"id '{frontmatter['id']}' must match name '{frontmatter['name']}'"))

    # Validate 'version' is semver
    if 'version' in frontmatter:
        if not validate_semver(str(frontmatter['version'])):
            errors.append(ValidationError(skill_md, f"Invalid version '{frontmatter['version']}': must be semver (X.Y.Z)"))

    # Validate 'license'
    if 'license' in frontmatter:
        if frontmatter['license'] not in VALID_LICENSES:
            errors.append(ValidationError(skill_md, f"Invalid license '{frontmatter['license']}': must be one of {VALID_LICENSES}", severity='warning'))

    # Validate 'description' structure
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if 'Use when:' not in desc:
            errors.append(ValidationError(skill_md, "description missing 'Use when:' section"))
        if 'NOT for:' not in desc:
            errors.append(ValidationError(skill_md, "description missing 'NOT for:' section"))

    # Validate 'mcpToolDependencies' structure
    if 'mcpToolDependencies' in frontmatter:
        deps = frontmatter['mcpToolDependencies']
        if not isinstance(deps, list):
            errors.append(ValidationError(skill_md, "mcpToolDependencies must be a list"))
        else:
            for i, dep in enumerate(deps):
                if not isinstance(dep, dict):
                    errors.append(ValidationError(skill_md, f"mcpToolDependencies[{i}] must be a dictionary"))
                    continue
                if 'server' not in dep:
                    errors.append(ValidationError(skill_md, f"mcpToolDependencies[{i}] missing 'server' field"))
                if 'tools' not in dep:
                    errors.append(ValidationError(skill_md, f"mcpToolDependencies[{i}] missing 'tools' field"))
                elif not isinstance(dep['tools'], list):
                    errors.append(ValidationError(skill_md, f"mcpToolDependencies[{i}].tools must be a list"))

    # Validate 'supportBoundary' structure
    if 'supportBoundary' in frontmatter:
        sb = frontmatter['supportBoundary']
        if not isinstance(sb, dict):
            errors.append(ValidationError(skill_md, "supportBoundary must be a dictionary"))
        else:
            if 'model' not in sb:
                errors.append(ValidationError(skill_md, "supportBoundary missing 'model' field"))

    return errors


def discover_skill_dirs(skills_dir: Path) -> List[Path]:
    """Every directory under skills/ that holds a SKILL.md.

    Discovery is by content rather than by directory name. A skill whose
    directory was renamed out of the 'aap-' convention must still be found, or
    neither the naming check nor the directory-name/front-matter agreement
    check can ever fire for it.
    """
    return sorted(d for d in skills_dir.iterdir()
                  if d.is_dir() and (d / 'SKILL.md').is_file())


def validate_docs_links(docs_dir: Path) -> List[ValidationError]:
    """Validate internal links within docs/ directory."""
    errors = []

    if not docs_dir.exists():
        return errors

    for doc_file in docs_dir.rglob('*.md'):
        content = doc_file.read_text(encoding='utf-8')

        # Find relative markdown links
        links = re.findall(r'\[.*?\]\(([^)]+\.md)\)', content)
        for link in links:
            # Skip external URLs
            if link.startswith('http://') or link.startswith('https://'):
                continue

            # Resolve relative to doc_file's directory
            link_path = (doc_file.parent / link).resolve()
            if not link_path.exists():
                errors.append(ValidationError(doc_file, f"Broken link: {link} does not exist"))

    return errors


def main():
    repo_root = Path(__file__).parent.parent
    skills_dir = repo_root / 'skills'
    docs_dir = repo_root / 'docs'

    all_errors = []

    print(f"\n{'='*70}")
    print("  AAP Skills Validation")
    print(f"{'='*70}\n")

    # Validate skills directory exists
    if not skills_dir.exists():
        print(f"{RED}✗ skills/ directory not found{RESET}")
        return 1

    # Find all skill directories
    skill_dirs = discover_skill_dirs(skills_dir)

    if not skill_dirs:
        print(f"{YELLOW}⚠ No skills found in skills/ directory{RESET}")
        return 0

    print(f"Validating {len(skill_dirs)} skill(s)...\n")

    # Validate each skill
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        all_errors.extend(errors)

        if errors:
            for error in errors:
                print(error)
        else:
            print(f"{GREEN}✓ {skill_dir.name}{RESET}")

    # Validate docs/ links
    print(f"\nValidating docs/ links...\n")
    docs_errors = validate_docs_links(docs_dir)
    all_errors.extend(docs_errors)

    if docs_errors:
        for error in docs_errors:
            print(error)
    else:
        print(f"{GREEN}✓ docs/ links{RESET}")

    # Summary
    print(f"\n{'='*70}")
    error_count = sum(1 for e in all_errors if e.severity == 'error')
    warning_count = sum(1 for e in all_errors if e.severity == 'warning')

    if error_count == 0 and warning_count == 0:
        print(f"{GREEN}✅ All validations passed!{RESET}")
        return 0
    else:
        if error_count > 0:
            print(f"{RED}❌ {error_count} error(s) found{RESET}")
        if warning_count > 0:
            print(f"{YELLOW}⚠ {warning_count} warning(s) found{RESET}")
        return 1 if error_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
