---
name: blog-content
description: "Generate SEO-optimized blog drafts from trend keywords. Input: trends JSON or single keyword. Output: markdown draft for wp-publisher. Use when creating blog content from trend-scanner results or any keyword-based draft generation."
allowed-tools: Read, Write, Bash, Glob
---

# Blog Content Skill

Generate SEO-optimized Korean blog drafts from trend keywords.

## Input

- `trends/daily_YYYY-MM-DD.json` (from trend-scanner)
- or a single keyword string

## Output

- `drafts/YYYY-MM-DD_keyword.md`
- `drafts/YYYY-MM-DD_keyword_meta.json`

## Workflow

1. **Analyze**
   - Load input keyword(s)
   - Classify intent: informational vs transactional
   - Classify category: government support / finance / tax / card / general
   - Estimate CPC band

2. **Draft**
   - Pick template by category:
     - `templates/moneybull.py` (default)
     - `templates/government.py`
     - `templates/finance.py`
     - `templates/tax.py`
   - Generate markdown + optional Gutenberg block JSON
   - Insert E-E-A-T style sentences if experience facts are available

3. **SEO**
   - Generate SEO title, meta description, focus keyword, internal link suggestions via `seo/meta_generator.py`

4. **Save**
   - Save `.md` and `_meta.json` to `output/`

## Integration

- `trend-scanner` → `blog-content` → `wp-publisher`
- Drafts are approved manually before publishing.
