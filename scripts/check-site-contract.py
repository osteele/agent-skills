#!/usr/bin/env python3
"""Check the published notebook schema copy against the skill authority."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "skills"
    / "research-lab-notebook"
    / "references"
    / "notebook-schema.json"
)
SITE_SCHEMA = Path("src/data/research-lab-notebook-schema.json")
SITE_REFERENCE = Path(
    "src/pages/reference/research-lab-notebook/reference/index.astro"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, help="Root of the notes site repository")
    args = parser.parse_args()

    site_schema_path = args.site.resolve() / SITE_SCHEMA
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    published = json.loads(site_schema_path.read_text(encoding="utf-8"))
    if source != published:
        print(f"ERROR: {site_schema_path} differs from {SOURCE}")
        return 1

    reference_path = args.site.resolve() / SITE_REFERENCE
    reference = reference_path.read_text(encoding="utf-8")
    expected_fragments = (
        "import notebookSchema",
        "notebookSchema.required_files",
        "notebookSchema.experiment_statuses",
        "notebookSchema.experiment_id.examples",
        "notebookSchema.plan.required_frontmatter",
        "notebookSchema.plan.status_directories",
        "notebookSchema.claim.columns",
        "notebookSchema.claim.roles",
        "notebookSchema.human_review.checkpoints",
        "notebookSchema.ledger.required_fields",
    )
    missing = [fragment for fragment in expected_fragments if fragment not in reference]
    if missing:
        print(f"ERROR: {reference_path} does not render: {', '.join(missing)}")
        return 1
    print("Published notebook contract matches the skill schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
