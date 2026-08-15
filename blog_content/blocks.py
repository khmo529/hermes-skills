from __future__ import annotations

from typing import Any


def _block_paragraph(text: str) -> dict:
    return {"blockName": "core/paragraph", "attrs": {}, "innerBlocks": [], "innerHTML": text}


def render_markdown_as_gutenberg_blocks(markdown_text: str) -> list[dict]:
    lines = markdown_text.splitlines()
    blocks: list[dict] = []
    buffer: list[str] = []

    def flush_paragraph() -> None:
        text = "\n".join(buffer).strip()
        if text:
            blocks.append(_block_paragraph(text))
        buffer.clear()

    for line in lines:
        if line.startswith("#"):
            flush_paragraph()
            blocks.append(_block_paragraph(line))
        elif line.startswith("- "):
            flush_paragraph()
            blocks.append(_block_paragraph(line))
        elif line.strip() == "":
            flush_paragraph()
        else:
            buffer.append(line)

    flush_paragraph()
    return blocks[:1] if not blocks else blocks
