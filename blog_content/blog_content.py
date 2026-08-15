import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from blog_content.seo.keyword_analyzer import analyze_keyword
from blog_content.templates.finance import render_finance_template
from blog_content.templates.government import render_government_template
from blog_content.templates.tax import render_tax_template


@dataclass
class DraftInput:
    keyword: str
    category: Optional[str] = None
    experience_notes: Optional[str] = None
    trend: Optional[Dict[str, Any]] = None
    reader_level: str = "중급"
    base_date: Optional[str] = None
    output_dir: Path = Path("output")


def _extract_title_from_html(html: str) -> str:
    match = re.search(r"<h2[^>]*id=[\"']([^\"']+)[\"'][^>]*>(.*?)</h2>", html, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return re.sub(r"<[^>]+>", "", match.group(2)).strip()
    match = re.search(r"<h2[^>]*>(.*?)</h2>", html, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return re.sub(r"<[^>]+>", "", match.group(1)).strip()
    return "Untitled"


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
    blocked_patterns = [
        (r"<!--\s*wp:", "wp 블록 주석"),
        (r"\bclass\s*=", "class 속성"),
        (r"\bstyle\s*=", "style 속성"),
        (r"colspan", "colspan 속성"),
        (r"rowspan", "rowspan 속성"),
        (r"첫째,", "금지 문구: 첫째"),
        (r"둘째,", "금지 문구: 둘째"),
        (r"결론적으로", "금지 문구: 결론적으로"),
        (r"~인 것이죠", "금지 문구: ~인 것이죠"),
        (r"~셈입니다", "금지 문구: ~셈입니다"),
        (r"알아보겠습니다", "금지 문구: 알아보겠습니다"),
        (r"말씀드리겠습니다", "금지 문구: 말씀드리겠습니다"),
        (r"라고 할 수 있습니다", "금지 문구: ~라고 할 수 있습니다"),
        (r"생각해볼 필요가 있습니다", "금지 문구: 생각해볼 필요가 있습니다"),
        (r"대박", "금지 문구: 대박"),
        (r"무조건", "금지 문구: 무조건"),
        (r"필수", "금지 문구: 필수"),
        (r"100%", "금지 문구: 100%"),
    ]
    required_patterns = [
        (r"<blockquote", "요약 박스(blockquote)"),
        (r"<table", "시뮬레이션/비교 테이블"),
        (r"<hr", "SEO 메타데이터 구분자(<hr>)"),
    ]
    lower = content.lower()
    found = [name for pat, name in blocked_patterns if re.search(pat, lower)]
    missing = [name for pat, name in required_patterns if not re.search(pat, lower)]
    if found or missing:
        msgs = []
        if found:
            msgs.append("BLOCKED: " + ", ".join(found))
        if missing:
            msgs.append("MISSING: " + ", ".join(missing))
        raise RuntimeError(" | ".join(msgs))
    return content


def _split_content(checked: str) -> Dict[str, str]:
    parts = re.split(r"<hr\s*/?>", checked, maxsplit=1, flags=re.IGNORECASE)
    html = parts[0].strip()
    meta = parts[1].strip() if len(parts) > 1 else ""
    return {"html": html, "meta": meta}


def _fallback_template(keyword: str, category: str) -> str:
    if category in {"정부지원금", "정책", "청년정책", "government"}:
        return render_government_template(keyword=keyword, analysis={}, experience_notes="")
    if category in {"절세", "세금", "tax"}:
        return render_tax_template(keyword=keyword, analysis={}, experience_notes="")
    if category in {"finance", "금융", "주식", "부동산", "코인", "투자", "환율", "경제정책", "moneybull"}:
        return render_finance_template(keyword=keyword, analysis={}, experience_notes="")
    return render_finance_template(keyword=keyword, analysis={}, experience_notes="")


def _generate_slug(keyword: str, title: str) -> str:
    category_slugs = {
        "tax": "tax",
        "tax-saving": "tax-saving",
        "cryptocurrency": "coin",
        "stock": "stock",
        "real-estate": "real-estate",
        "pension": "pension",
        "forex": "exchange-rate",
        "credit-card": "card",
        "government-policy": "policy",
        "account": "account",
        "finance": "finance",
    }
    base = category_slugs.get(_auto_category(keyword), "guide")
    keyword_map = {
        "코인": "coin", "세금": "tax", "신고": "report",
        "절세": "tax-saving", "IRP": "irp", "환율": "exchange-rate",
        "주식": "stock", "부동산": "real-estate", "연금": "pension",
        "카드": "card",
    }
    extras = []
    for k, v in keyword_map.items():
        if (k in keyword or k in title) and v != base and v not in extras:
            extras.append(v)
    parts = [base] + extras[:2]
    return "-".join(parts)


def _auto_category(keyword: str) -> str:
    keyword_to_category = {
        "코인": "cryptocurrency", "주식": "stock", "부동산": "real-estate",
        "IRP": "pension", "연금": "pension", "세금": "tax", "절세": "tax",
        "환율": "forex", "카드": "credit-card", "지원금": "government-policy",
        "계좌": "account",
    }
    for k, v in keyword_to_category.items():
        if k in keyword:
            return v
    return "finance"


def _generate_tags(keyword: str, title: str) -> list[str]:
    base_tags = ["재테크", "돈벌이", "금융", "투자", "절약"]
    keyword_map = {
        "코인": ["코인", "암호화폐", "가상화폐", "비트코인"],
        "세금": ["세금", "소득세", "양도세", "종합소득세"],
        "IRP": ["IRP", "연금저축", "퇴직연금"],
        "환율": ["환율", "달러", "원화", "외환"],
        "주식": ["주식", "배당", "ETF"],
    }
    keyword_tags = []
    for k, tags in keyword_map.items():
        if k in keyword or k in title:
            keyword_tags.extend(tags)
    all_tags = list(dict.fromkeys(keyword_tags + base_tags))
    return all_tags[:12]


def _generate_meta(keyword: str, title: str, content: str) -> dict[str, str]:
    focus = keyword.strip()
    seo_title = title[:57] + "..." if len(title) > 60 else title
    text = re.sub(r"<[^>]+>", "", content)
    first_sentence = text.split(".")[0][:150]
    seo_description = first_sentence + "..." if len(first_sentence) > 140 else first_sentence
    return {
        "focus_keyword": focus,
        "seo_title": seo_title,
        "seo_description": seo_description,
        "rank_math_focus_keyword": focus,
        "rank_math_title": seo_title,
        "rank_math_description": seo_description,
        "_yoast_wpseo_focuskw": focus,
        "_yoast_wpseo_title": seo_title,
        "_yoast_wpseo_metadesc": seo_description,
    }


def _check_length(html: str) -> bool:
    text = re.sub(r"<[^>]+>", "", html)
    length = len(text.strip())
    return 1500 <= length <= 2500


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

    title = _extract_title_from_html(content) or f"2026 {keyword} 신청 자격 및 방법 | 한눈에 보기"
    auto_cat = _auto_category(keyword)
    category = category or auto_cat
    slug = _generate_slug(keyword, title)
    tags = _generate_tags(keyword, title)
    generated_meta = _generate_meta(keyword, title, content)
    plain_length = len(re.sub(r"<[^>]+>", "", content).strip())
    length_ok = _check_length(content)
    meta = {
        "focus_keyword": keyword,
        "category": category,
        "intent": analysis.get("intent"),
        "cpc_band": analysis.get("cpc_band"),
        "meta_block": meta_block,
        "trend": trend,
        "slug": slug,
        "tags": tags,
        "seo_title": generated_meta["seo_title"],
        "seo_description": generated_meta["seo_description"],
        "rank_math_focus_keyword": generated_meta["rank_math_focus_keyword"],
        "rank_math_title": generated_meta["rank_math_title"],
        "rank_math_description": generated_meta["rank_math_description"],
        "_yoast_wpseo_focuskw": generated_meta["_yoast_wpseo_focuskw"],
        "_yoast_wpseo_title": generated_meta["_yoast_wpseo_title"],
        "_yoast_wpseo_metadesc": generated_meta["_yoast_wpseo_metadesc"],
        "plain_length": plain_length,
        "length_ok": length_ok,
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
