#!/usr/bin/env python3
"""Validate the curated PPTX assets and their template catalog."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_DIR / "references" / "template-catalog.json"


def pptx_slide_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"corrupt ZIP member: {bad_member}")
        return sum(
            1
            for name in archive.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        )


def main() -> int:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    ids: set[str] = set()

    for template in catalog["templates"]:
        template_id = template["id"]
        if template_id in ids:
            errors.append(f"{template_id}: duplicate id")
        ids.add(template_id)

        asset = SKILL_DIR / template["asset"]
        preview = SKILL_DIR / template["preview"]
        if not asset.is_file():
            errors.append(f"{template_id}: missing asset {asset}")
            continue
        if not preview.is_file():
            errors.append(f"{template_id}: missing preview {preview}")

        try:
            count = pptx_slide_count(asset)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{template_id}: cannot validate PPTX: {exc}")
            continue

        expected = len(template["source_slides"])
        if count != expected:
            errors.append(f"{template_id}: PPTX has {count} slides, catalog maps {expected}")

        for role, slide_numbers in template["slide_roles"].items():
            for slide_number in slide_numbers:
                if not 1 <= slide_number <= count:
                    errors.append(
                        f"{template_id}: role {role} references invalid asset slide {slide_number}"
                    )

    default_ids = catalog["defaults"]["templates"]
    for template_id in default_ids:
        if template_id not in ids:
            errors.append(f"default template is missing: {template_id}")

    if errors:
        print("Template bank validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Template bank OK: {len(ids)} templates, {sum(len(t['source_slides']) for t in catalog['templates'])} curated slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
