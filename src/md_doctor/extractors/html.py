"""HTML 태그 추출기 — 마크다운 본문에서 raw HTML 을 파싱.

순수 함수. 부수효과 없음.
- 자체닫힘/쌍 태그 모두 지원
- 코드펜스/인라인 코드 내부 제외 (fences 인자)
- v0.3.0: <img>, <a>, <div>, <span>, <p>, <br> 등 일반 태그
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

from md_doctor.extractors.code_fence import CodeFence, is_in_code_region


@dataclass(frozen=True)
class HtmlRef:
    """HTML 태그 한 개."""

    tag: str
    line: int
    col: int
    attrs: dict[str, str]
    kind: str = "inline"


# 자체닫힘 또는 일반 태그 시작/끝: <tag ...> or <tag ... />
_TAG_RE = re.compile(
    r"<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)/?>", re.DOTALL
)

# 쌍 태그: <tag ...>content</tag>
_PAIRED_RE = re.compile(
    r"<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)>(.*?)</\1>", re.DOTALL
)

_ATTR_RE = re.compile(r'([a-zA-Z][a-zA-Z0-9_-]*)\s*=\s*"([^"]*)"')

_BLOCK_TAGS = frozenset({"div", "p", "section", "article", "pre", "blockquote"})


def _parse_attrs(attr_str: str) -> dict[str, str]:
    """속성 문자열을 dict 로."""
    return {m.group(1): m.group(2) for m in _ATTR_RE.finditer(attr_str)}


def _is_block_tag(tag: str) -> bool:
    """블록 수준 태그."""
    return tag in _BLOCK_TAGS


def _offset_to_line_col(text: str, offset: int) -> tuple[int, int]:
    """text 의 offset → (1-based line, 1-based col)."""
    line = text.count("\n", 0, offset) + 1
    last_nl = text.rfind("\n", 0, offset)
    col = offset - last_nl if last_nl >= 0 else offset + 1
    return line, col


def _strip_inline_code(line: str) -> str:
    """인라인 코드 영역을 공백으로 (위치 보존)."""
    out: list[str] = []
    in_code = False
    for ch in line:
        if ch == "`":
            in_code = not in_code
            out.append(" ")
        elif in_code:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def _line_has_inline_code_at(line: str, col: int) -> bool:
    """해당 col 위치가 인라인 코드 내부인지."""
    masked = _strip_inline_code(line)
    if col - 1 >= len(masked):
        return False
    return masked[col - 1] == " "


def extract_html_refs(
    text: str,
    lines: list[str],
    fences: list[CodeFence],
) -> list[HtmlRef]:
    """마크다운에서 HTML 태그를 추출. 코드 영역 제외.

    Parameters
    ----------
    text:
        원본 마크다운.
    lines:
        ``text.splitlines()`` 와 동등.
    fences:
        ``mark_code_regions(lines)`` 결과. 코드 영역 판별용.
    """
    refs: list[HtmlRef] = []
    seen: set[tuple[int, int, str]] = set()

    # 1. 쌍 태그 먼저 (multi-line 가능)
    for m in _PAIRED_RE.finditer(text):
        tag = m.group(1).lower()
        attr_str = m.group(2)
        start_offset = m.start()
        line, col = _offset_to_line_col(text, start_offset)
        if is_in_code_region(line, fences):
            continue
        # 인라인 코드 내부 스킵
        if line - 1 < len(lines) and _line_has_inline_code_at(lines[line - 1], col):
            continue
        key = (line, col, tag)
        if key in seen:
            continue
        seen.add(key)
        refs.append(
            HtmlRef(
                tag=tag,
                line=line,
                col=col,
                attrs=_parse_attrs(attr_str),
                kind="block" if _is_block_tag(tag) else "inline",
            )
        )

    # 2. 자체닫힘 또는 쌍의 시작
    for m in _TAG_RE.finditer(text):
        tag = m.group(1).lower()
        attr_str = m.group(2)
        offset = m.start()
        line, col = _offset_to_line_col(text, offset)
        if is_in_code_region(line, fences):
            continue
        if line - 1 < len(lines) and _line_has_inline_code_at(lines[line - 1], col):
            continue
        key = (line, col, tag)
        if key in seen:
            continue
        seen.add(key)
        refs.append(
            HtmlRef(
                tag=tag,
                line=line,
                col=col,
                attrs=_parse_attrs(attr_str),
                kind="block" if _is_block_tag(tag) else "inline",
            )
        )

    refs.sort(key=lambda r: (r.line, r.col))
    return refs
