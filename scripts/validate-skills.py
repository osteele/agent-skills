#!/usr/bin/env python3
"""Validate repository skill structure without third-party dependencies."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PRIVATE_PATTERNS = (
    "/Users/",
    "cool30",
    "cool100",
    "studio-agent",
    "AUGUR",
    "llm-performance-models",
)
NOTEBOOK_SKILL = SKILLS / "research-lab-notebook"
NOTEBOOK_SCHEMA = NOTEBOOK_SKILL / "references" / "notebook-schema.json"


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    problems: list[str] = []
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        problems.append("no skills found")
    for directory in skill_dirs:
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            problems.append(f"{directory.name}: missing SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        metadata = frontmatter(text)
        if set(metadata) != {"name", "description"}:
            problems.append(
                f"{directory.name}: frontmatter keys must be name and description"
            )
        name = metadata.get("name", "")
        if name != directory.name or not NAME_RE.fullmatch(name):
            problems.append(f"{directory.name}: invalid or mismatched skill name {name!r}")
        if len(metadata.get("description", "")) < 40:
            problems.append(f"{directory.name}: description is too short")
        if "TODO" in text:
            problems.append(f"{directory.name}: contains TODO placeholder")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#")):
                continue
            path = directory / target.split("#", 1)[0]
            if not path.exists():
                problems.append(f"{directory.name}: broken link {target}")

    if not NOTEBOOK_SCHEMA.is_file():
        problems.append("research-lab-notebook: missing canonical notebook schema")
    else:
        schema = json.loads(NOTEBOOK_SCHEMA.read_text(encoding="utf-8"))
        template_root = NOTEBOOK_SKILL / "assets" / "lab-notebook"
        for relative_path in schema["required_files"]:
            if not (template_root / relative_path).is_file():
                problems.append(
                    "research-lab-notebook: starter template is missing "
                    f"{relative_path}"
                )

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PRIVATE_PATTERNS:
            if pattern in text:
                problems.append(f"{path.relative_to(ROOT)}: private pattern {pattern!r}")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print(f"Validated {len(skill_dirs)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
