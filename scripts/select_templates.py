#!/usr/bin/env python3
"""Select three complementary HFUT templates and produce a slide-source plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = SKILL_DIR / "references" / "template-catalog.json"

SIGNALS = {
    "formality": ["答辩", "论文", "研究", "正式", "领导", "审查", "汇报", "defense", "research", "formal"],
    "data": ["数据", "图表", "分析", "结果", "统计", "表格", "市场", "data", "chart", "analysis"],
    "image": ["图片", "摄影", "校园", "介绍", "人文", "故事", "photo", "campus", "story"],
    "minimal": ["简洁", "极简", "清爽", "现代", "高级", "minimal", "clean", "modern", "premium"],
    "dark": ["深色", "沉稳", "科技", "工程", "dark", "technology", "engineering"],
    "seasonal": ["冬季", "冬天", "雪", "秋季", "秋天", "橙色", "季节", "winter", "autumn", "snow"],
}

DEFAULT_BASE = {
    "academic-clean": 5.0,
    "analytical-clean": 4.0,
    "campus-photo": 3.5,
    "campus-arc": 3.0,
    "premium-overlay": 2.5,
}


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_catalog(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def signal_strength(brief: str) -> dict[str, int]:
    lowered = brief.lower()
    return {
        dimension: sum(1 for word in words if word.lower() in lowered)
        for dimension, words in SIGNALS.items()
    }


def semantic_score(template: dict[str, Any], brief: str, signals: dict[str, int]) -> tuple[float, list[str]]:
    lowered = brief.lower()
    score = DEFAULT_BASE.get(template["id"], 1.0)
    hits: list[str] = []

    for keyword in template.get("keywords", []):
        if keyword.lower() in lowered:
            score += 4.0
            hits.append(keyword)

    for tag in template.get("tags", []):
        if tag.lower() in lowered:
            score += 2.0
            hits.append(tag)

    for dimension, strength in signals.items():
        if strength:
            score += strength * (template["scores"].get(dimension, 0) / 5.0) * 2.2

    if not signals["seasonal"] and template["scores"].get("seasonal", 0) >= 5:
        score -= 5.0

    return score, hits


def style_distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    dimensions = ("formality", "data", "image", "minimal", "dark", "seasonal")
    total = sum(abs(a["scores"].get(key, 0) - b["scores"].get(key, 0)) for key in dimensions)
    return total / (len(dimensions) * 5.0)


def compatibility(a: dict[str, Any], b: dict[str, Any]) -> float:
    formal_gap = abs(a["scores"]["formality"] - b["scores"]["formality"])
    dark_gap = abs(a["scores"]["dark"] - b["scores"]["dark"])
    return 3.0 - formal_gap * 0.35 - dark_gap * 0.2


def select_three(
    templates: list[dict[str, Any]],
    brief: str,
    includes: list[str],
    excludes: list[str],
) -> tuple[list[dict[str, Any]], dict[str, tuple[float, list[str]]]]:
    by_id = {template["id"]: template for template in templates}
    unknown = [item for item in includes + excludes if item not in by_id]
    if unknown:
        raise ValueError(f"Unknown template id(s): {', '.join(unknown)}")
    if len(set(includes)) > 3:
        raise ValueError("--include accepts at most three distinct template ids")
    overlap = sorted(set(includes) & set(excludes))
    if overlap:
        raise ValueError(f"Template ids cannot be both included and excluded: {', '.join(overlap)}")

    candidates = [template for template in templates if template["id"] not in set(excludes)]
    if len(candidates) < 3:
        raise ValueError("Fewer than three templates remain after exclusions")

    signals = signal_strength(brief)
    scored = {template["id"]: semantic_score(template, brief, signals) for template in candidates}

    if includes:
        anchor = by_id[includes[0]]
    else:
        anchor = max(candidates, key=lambda item: scored[item["id"]][0])

    selected = [anchor]
    forced_remaining = [by_id[item] for item in includes[1:] if item != anchor["id"]]

    while len(selected) < 3:
        if forced_remaining:
            choice = forced_remaining.pop(0)
        else:
            remaining = [item for item in candidates if item["id"] not in {x["id"] for x in selected}]

            def donor_score(candidate: dict[str, Any]) -> float:
                base = scored[candidate["id"]][0] * 0.62
                diversity = sum(style_distance(candidate, item) for item in selected) / len(selected)
                fit = sum(compatibility(candidate, item) for item in selected) / len(selected)

                selected_data = max(item["scores"]["data"] for item in selected)
                selected_image = max(item["scores"]["image"] for item in selected)
                missing_bonus = 0.0
                if selected_data < 4:
                    missing_bonus += candidate["scores"]["data"] * 0.8
                if selected_image < 4:
                    missing_bonus += candidate["scores"]["image"] * 0.8
                if selected_data >= 4 and selected_image >= 4:
                    missing_bonus += candidate["scores"]["minimal"] * 0.35

                seasonal_penalty = 0.0
                if not signals["seasonal"] and candidate["scores"]["seasonal"] >= 5:
                    seasonal_penalty = 4.0

                return base + diversity * 5.0 + fit + missing_bonus - seasonal_penalty

            choice = max(remaining, key=donor_score)
        if choice["id"] not in {item["id"] for item in selected}:
            selected.append(choice)

    return selected, scored


def distribute(total: int, groups: int) -> list[int]:
    base, extra = divmod(total, groups)
    return [base + (1 if index < extra else 0) for index in range(groups)]


def make_role_sequence(slides: int, sections: int) -> list[str]:
    if slides < 6:
        raise ValueError("A fused deck needs at least six slides")
    middle = slides - 4
    section_count = max(1, min(sections, middle // 2))
    chapter_sizes = distribute(middle, section_count)
    detail_cycle = ["content", "content", "process", "comparison", "data"]

    roles = ["cover", "agenda"]
    detail_index = 0
    for chapter_size in chapter_sizes:
        roles.append("section")
        for _ in range(chapter_size - 1):
            roles.append(detail_cycle[detail_index % len(detail_cycle)])
            detail_index += 1
    roles.extend(["summary", "closing"])
    return roles[:slides]


def choose_donor(
    role: str,
    position: int,
    selected: list[dict[str, Any]],
) -> dict[str, Any]:
    anchor, layout, accent = selected
    if role in {"cover", "agenda", "section", "closing"}:
        return anchor
    if role in {"process", "comparison"}:
        return layout
    if role == "data":
        return max((layout, accent), key=lambda item: item["scores"]["data"])
    if role == "summary":
        return anchor

    cycle = [anchor, layout, anchor, accent, layout]
    return cycle[position % len(cycle)]


def choose_asset_slide(
    template: dict[str, Any],
    role: str,
    counters: dict[tuple[str, str], int],
) -> int:
    roles = template["slide_roles"]
    candidates = roles.get(role) or roles.get("content") or [1]
    key = (template["id"], role)
    index = counters.get(key, 0)
    counters[key] = index + 1
    return candidates[index % len(candidates)]


def explain_role(template: dict[str, Any], role: str, hits: list[str]) -> str:
    reasons = template.get("best_for", [])[:2]
    if hits:
        reasons.insert(0, f"命中关键词：{'、'.join(hits[:3])}")
    role_label = {
        "visual_anchor": "负责统一品牌、字体、色彩和页眉页脚",
        "layout_donor": "负责流程、对比和复杂图文布局",
        "accent_donor": "负责数据、摄影或强调页面",
    }[role]
    return f"{role_label}；{'；'.join(reasons)}"


def build_plan(
    catalog: dict[str, Any],
    selected: list[dict[str, Any]],
    scored: dict[str, tuple[float, list[str]]],
    brief: str,
    slides: int,
    sections: int,
) -> dict[str, Any]:
    role_names = ["visual_anchor", "layout_donor", "accent_donor"]
    selected_output = []
    for role_name, template in zip(role_names, selected):
        score, hits = scored[template["id"]]
        selected_output.append(
            {
                "role": role_name,
                "id": template["id"],
                "display_name": template["display_name"],
                "asset": template["asset"],
                "preview": template["preview"],
                "score": round(score, 2),
                "palette": template["palette"],
                "fonts": template["fonts"],
                "why": explain_role(template, role_name, hits),
            }
        )

    counters: dict[tuple[str, str], int] = {}
    role_sequence = make_role_sequence(slides, sections)
    slide_plan = []
    for index, role in enumerate(role_sequence, start=1):
        donor = choose_donor(role, index, selected)
        asset_slide = choose_asset_slide(donor, role, counters)
        source_slide = donor["source_slides"][asset_slide - 1]
        slide_plan.append(
            {
                "output_slide": index,
                "purpose": role,
                "donor_template": donor["id"],
                "donor_asset": donor["asset"],
                "donor_asset_slide": asset_slide,
                "original_source_file": donor["source_file"],
                "original_source_slide": source_slide,
                "restyle_to_anchor": donor["id"] != selected[0]["id"],
            }
        )

    return {
        "catalog_version": catalog["version"],
        "brief": brief,
        "slides": slides,
        "sections": sections,
        "fusion_rule": catalog["defaults"]["visual_influence"],
        "templates": selected_output,
        "slide_plan": slide_plan,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, help="Topic, audience, use case, and visual preference")
    parser.add_argument("--slides", type=int, default=12)
    parser.add_argument("--sections", type=int, default=3)
    parser.add_argument("--include", help="Comma-separated template ids that must be selected")
    parser.add_argument("--exclude", help="Comma-separated template ids to exclude")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, help="Write the plan as UTF-8 JSON")
    args = parser.parse_args()

    catalog = load_catalog(args.catalog)
    selected, scored = select_three(
        catalog["templates"],
        args.brief,
        parse_csv(args.include),
        parse_csv(args.exclude),
    )
    plan = build_plan(catalog, selected, scored, args.brief, args.slides, args.sections)
    rendered = json.dumps(plan, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(args.output.resolve())
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
