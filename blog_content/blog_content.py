import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from blog_content.seo.keyword_analyzer import analyze_keyword
from blog_content.templates.government import render_government_template


@dataclass
class DraftInput:
    keyword: str
    category: Optional[str] = None
    experience_notes: Optional[str] = None
    trend: Optional[Dict[str, Any]] = None
    reader_level: str = "중급"
    base_date: Optional[str] = None
    output_dir: Path = Path("output")


def _extract_title_from_markdown(markdown_text: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown_text, flags=re.MULTILINE)
    return (match.group(1).strip() if match else "Untitled").strip()


def _today() -> str:
    return date.today().isoformat()


def _load_prompt_template() -> str:
    prompt_path = Path(__file__).resolve().parent / "prompts" / "draft_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def _build_prompt(item: Dict[str, Any]) -> str:
    keyword = item.get("keyword") or item.get("title") or ""
    category = item.get("category") or "moneybull"
    trend_data = item.get("trend") or {}
    experience_notes = item.get("experience_notes") or ""

    intent = analyze_keyword(keyword)
    intent_label = intent.get("intent", "정보형")
    reader_level = item.get("reader_level", "중급")
    base_date = item.get("base_date") or _today()

    template = _load_prompt_template()
    prompt = (
        template.replace("{{KEYWORD}}", keyword)
        .replace("{{CATEGORY}}", category)
        .replace("{{INTENT}}", intent_label)
        .replace("{{READER_LEVEL}}", reader_level)
        .replace("{{BASE_DATE}}", base_date)
        .replace("{{EXPERIENCE_NOTES}}", experience_notes)
        .replace("{{TREND_DATA}}", json.dumps(trend_data, ensure_ascii=False))
    )
    return prompt


def _call_ai(prompt: str) -> str:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI API 키가 설정되어 있지 않습니다. OPENAI_API_KEY 또는 ANTHROPIC_API_KEY를 설정하세요.")

    model = os.environ.get("AI_MODEL", "gpt-4o-mini")
    content = ""
    if api_key.startswith("sk-"):
        try:
            import openai
            openai.api_key = api_key
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "당신은 MoneyBull 블로그 메인 필진입니다. 규칙을 정확히 따르세요."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content or ""
        except Exception as exc:
            raise RuntimeError(f"AI 호출 실패: {exc}")
    else:
        raise RuntimeError("지원하지 않는 AI API 키 형식입니다.")

    if not content.strip():
        raise RuntimeError("AI 응답이 비어 있습니다.")
    return content


def _quality_check(content: str) -> str:
    banned = [
        "첫째,", "둘째,", "결론적으로", "~인 것이죠", "~셈입니다", "알아보겠습니다",
        "말씀드리겠습니다", "라고 할 수 있습니다", "생각해볼 필요가 있습니다", "대박", "무조건", "필수", "100%",
    ]
    lower = content.lower()
    found = [b for b in banned if b in lower]
    if found:
        raise RuntimeError(f"금지 문구 발견: {found}")

    if "blockquote" not in content.lower() and "<blockquote" not in content.lower():
        raise RuntimeError("요약 박스(blockquote)가 없습니다.")
    if "<table" not in content.lower():
        raise RuntimeError("시뮬레이션/비교 테이블이 없습니다.")
    if "<hr>" not in content:
        raise RuntimeError("SEO 메타데이터 구분자(<hr>)가 없습니다.")
    return content


def _split_content(checked: str) -> Dict[str, str]:
    parts = re.split(r"<hr\s*/?>", checked, maxsplit=1, flags=re.IGNORECASE)
    html = parts[0].strip()
    meta = parts[1].strip() if len(parts) > 1 else ""
    return {"html": html, "meta": meta}


def _fallback_template(keyword: str, category: str) -> str:
    if category in {"정부지원금", "정책", "청년정책", "절세", "세금"}:
        return render_government_template(keyword=keyword, analysis={}, experience_notes="")
    return "<p>MoneyBull 규칙 기반 초안을 생성하려면 AI API 키가 필요합니다.</p>"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_draft(item: Dict[str, Any]) -> Dict[str, Any]:
    keyword = item.get("keyword") or item.get("title") or ""
    category = item.get("category") or "moneybull"
    experience_notes = item.get("experience_notes")
    trend = item.get("trend") or {}

    analysis = analyze_keyword(keyword)
    analysis["category"] = category
    analysis["intent"] = (
        "transactional" if category in {"government", "finance", "tax"} else analysis.get("intent", "informational")
    )

    ai_available = bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("AI_API_KEY"))
    if ai_available:
        prompt = _build_prompt({**item, "category": category, "experience_notes": experience_notes, "trend": trend})
        try:
            raw = _call_ai(prompt)
            checked = _quality_check(raw)
            splitted = _split_content(checked)
            content = splitted["html"]
            meta_block = splitted["meta"]
        except Exception:
            content = _fallback_template(keyword, category)
            meta_block = ""
    else:
        content = _fallback_template(keyword, category)
        meta_block = ""

    title = _extract_title_from_markdown(content) or f"2026 {keyword} 신청 자격 및 방법 | 한눈에 보기"
    meta = {
        "focus_keyword": keyword,
        "category": category,
        "intent": analysis.get("intent"),
        "cpc_band": analysis.get("cpc_band"),
        "meta_block": meta_block,
        "trend": trend,
    }

    return {
        "keyword": keyword,
        "category": category,
        "title": title,
        "content": content,
        "analysis": analysis,
        "meta": meta,
        "trend": trend,
    }


def save_draft(keyword: str, draft: Dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    today = _today()
    slug = keyword.replace(" ", "-")[:60]
    _ensure_dir(output_dir)

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
    except Exception as exc:
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
    parser = argparse.ArgumentParser(description="MoneyBull SEO blog draft generator")
    parser.add_argument("input", nargs="?", help="keyword string or path to trends JSON")
    parser.add_argument("--category", default=None)
    parser.add_argument("--experience", default=None)
    parser.add_argument("--reader-level", default="중급")
    parser.add_argument("--base-date", default=None)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--publish", action="store_true", help="publish generated draft via wp-publisher")
    args = parser.parse_args()

    if not args.input:
        raise SystemExit("input keyword or trends JSON is required")

    items = []
    if os.path.isfile(args.input):
        path = Path(args.input)
        data = json.loads(path.read_text(encoding="utf-8"))
        items = [data] if isinstance(data, dict) else data
    else:
        items = [{
            "keyword": args.input,
            "category": args.category,
            "experience_notes": args.experience,
            "reader_level": args.reader_level,
            "base_date": args.base_date,
        }]

    output_dir = Path(args.output_dir)
    results = []
    for item in items:
        if args.category and not item.get("category"):
            item["category"] = args.category
        if args.experience and not item.get("experience_notes"):
            item["experience_notes"] = args.experience
        if args.reader_level and not item.get("reader_level"):
            item["reader_level"] = args.reader_level
        if args.base_date and not item.get("base_date"):
            item["base_date"] = args.base_date

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
