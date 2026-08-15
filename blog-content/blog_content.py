import argparse
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from seo.keyword_analyzer import analyze_keyword
from seo.meta_generator import generate_seo_metadata
from templates.government import render_government_template


@dataclass
class DraftInput:
    keyword: str
    category: Optional[str] = None
    experience_notes: Optional[str] = None
    output_dir: Path = Path("output")


TEMPLATE_MAP = {
    "government": render_government_template,
    "finance": None,
    "tax": None,
    "moneybull": render_government_template,
}


def load_trends_file(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return [data]
    return data


def generate_draft(item: dict) -> str:
    keyword = item.get("keyword") or item.get("title") or ""
    category = item.get("category") or "moneybull"
    experience_notes = item.get("experience_notes")

    analysis = analyze_keyword(keyword)
    analysis["category"] = category
    analysis["intent"] = (
        "transactional" if category in {"government", "finance", "tax"} else analysis.get("intent", "informational")
    )
    template_fn = TEMPLATE_MAP.get(category) or TEMPLATE_MAP["moneybull"]

    body = template_fn(
        keyword=keyword,
        analysis=analysis,
        experience_notes=experience_notes,
    )
    meta = generate_seo_metadata(keyword, analysis, body)
    return body, meta


def save_draft(keyword: str, body: str, meta: dict, output_dir: Path) -> tuple[Path, Path]:
    today = date.today().isoformat()
    slug = keyword.replace(" ", "-")[:60]
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f"{today}_{slug}.md"
    md_path.write_text(body, encoding="utf-8")

    meta_path = output_dir / f"{today}_{slug}_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return md_path, meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SEO-optimized blog draft from keyword or trends JSON")
    parser.add_argument("input", nargs="?", help="keyword string or path to trends JSON")
    parser.add_argument("--category", default=None)
    parser.add_argument("--experience", default=None)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    if not args.input:
        raise SystemExit("input keyword or trends JSON is required")

    items = []
    if os.path.isfile(args.input):
        items = load_trends_file(args.input)
    else:
        items = [{"keyword": args.input, "category": args.category, "experience_notes": args.experience}]

    output_dir = Path(args.output_dir)
    results = []
    for item in items:
        if args.category and not item.get("category"):
            item["category"] = args.category
        if args.experience and not item.get("experience_notes"):
            item["experience_notes"] = args.experience
        body, meta = generate_draft(item)
        md_path, meta_path = save_draft(item.get("keyword", "draft"), body, meta, output_dir)
        results.append({"keyword": item.get("keyword"), "md": str(md_path), "meta": str(meta_path)})

    print(json.dumps({"created": len(results), "files": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
