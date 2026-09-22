#!/usr/bin/env python3
"""
Validate AAP skills against the content type definition.

Checks:
- Directory structure (skills/aap-{name}/SKILL.md)
- YAML front matter parsing
- Required fields (agentskills.io + Red Hat Skill fields)
- Field constraints (kebab-case, semver, etc.)
- Description structure (Use when, NOT for)
- Internal links
"""

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


class ValidationError:
    def __init__(self, skill_path: Path, message: str, severity: str = 'error'):
        self.skill_path = skill_path
        self.message = message
        self.severity = severity

    def __str__(self):
        color = RED if self.severity == 'error' else YELLOW
        symbol = '✗' if self.severity == 'error' else '⚠'
        return f"{color}{symbol} {self.skill_path.parent.name}: {self.message}{RESET}"


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

    parts = content.split('---\n', 2)
    if len(parts) < 3:
        errors.append(ValidationError(skill_md, "Missing closing front matter delimiter (----)"))
        return {}, "", errors

    frontmatter_str = parts[1]
    body = parts[2]

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


def validate_skill(skill_dir: Path) -> List[ValidationError]:
    """Validate a single skill directory."""
    errors = []
    skill_md = skill_dir / 'SKILL.md'

    # Check SKILL.md exists
    if not skill_md.exists():
        errors.append(ValidationError(skill_md, "SKILL.md not found"))
        return errors

    # Parse front matter
    frontmatter, body, parse_errors = parse_skill_frontmatter(skill_md)
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

    # Validate internal references/ links in body
    references_dir = skill_dir / 'references'
    if references_dir.exists():
        # Find markdown links to references/
        ref_links = re.findall(r'\[.*?\]\((references/[^)]+)\)', body)
        for link in ref_links:
            link_path = skill_dir / link
            if not link_path.exists():
                errors.append(ValidationError(skill_md, f"Broken link: {link} does not exist"))

    return errors


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

    # Find all skill directories (aap-*)
    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir() and d.name.startswith('aap-')])

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
