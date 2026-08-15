import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from blog_content.seo.keyword_analyzer import analyze_keyword
from blog_content.seo.meta_generator import generate_seo_metadata
from blog_content.templates.government import render_government_template


@dataclass
class DraftInput:
    keyword: str
    category: Optional[str] = None
    experience_notes: Optional[str] = None
    trend: Optional[Dict[str, Any]] = None
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


def _extract_title_from_markdown(markdown_text: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown_text, flags=re.MULTILINE)
    return (match.group(1).strip() if match else "Untitled").strip()


def generate_draft(item: Dict[str, Any]) -> Dict[str, Any]:
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

    return {
        "keyword": keyword,
        "category": category,
        "title": _extract_title_from_markdown(body),
        "content": body,
        "analysis": analysis,
        "meta": meta,
        "trend": item.get("trend"),
    }


def save_draft(keyword: str, draft: Dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    today = date.today().isoformat()
    slug = keyword.replace(" ", "-")[:60]
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f"{today}_{slug}.md"
    md_path.write_text(draft.get("content", ""), encoding="utf-8")

    meta_payload = {
        "keyword": keyword,
        "title": draft.get("title"),
        "category": draft.get("category"),
        "analysis": draft.get("analysis"),
        "meta": draft.get("meta"),
        "md": str(md_path),
    }
    meta_path = output_dir / f"{today}_{slug}_meta.json"
    meta_path.write_text(json.dumps(meta_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return md_path, meta_path


def publish_draft(draft: Dict[str, Any], status: str = "draft") -> Dict[str, Any]:
    try:
        from wp_publisher.wp_publisher import WPPublisher
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"wp-publisher import failed: {exc}")

    publisher = WPPublisher()
    post_id = publisher.create_draft(
        title=draft.get("title") or draft.get("keyword", "Untitled"),
        content=draft.get("content", ""),
        category=draft.get("category"),
        status=status,
        excerpt=draft.get("meta", {}).get("meta_description"),
    )
    return {"post_id": post_id, "title": draft.get("title"), "category": draft.get("category")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SEO-optimized blog draft from keyword or trends JSON")
    parser.add_argument("input", nargs="?", help="keyword string or path to trends JSON")
    parser.add_argument("--category", default=None)
    parser.add_argument("--experience", default=None)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--publish", action="store_true", help="publish generated draft via wp-publisher")
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
        draft = generate_draft(item)
        md_path, meta_path = save_draft(item.get("keyword", "draft"), draft, output_dir)
        record = {
            "keyword": item.get("keyword"),
            "title": draft.get("title"),
            "category": draft.get("category"),
            "md": str(md_path),
            "meta": str(meta_path),
        }
        if args.publish:
            publish_result = publish_draft(draft, status="draft")
            record.update(publish_result)
        results.append(record)

    print(json.dumps({"created": len(results), "files": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
