"""링크 참조 추출기 — 마크다운 본문에서 모든 링크 형태를 파싱.

순수 함수. 부수효과 없음. 디스크/네트워크 미사용.
- 인라인 링크: [text](url "title")
- 참조 링크: [text][ref] + [ref]: url
- 단축 참조: [ref] + [ref]: url
- 자동 링크: <https://...>, <foo@bar.com>
- 정의 자체도 kind="definition" 으로 추출 (참조 해결용)
- 코드펜스/인라인 코드 내부 제외
- mailto:/data:/javascript:/fragment-only 스킵
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LinkRef:
    """마크다운에서 추출한 단일 링크 참조."""

    target: str
    line: int
    col: int
    text: str = ""
    kind: str = "inline"


_INLINE_RE = re.compile(
    r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
)

_REFERENCE_RE = re.compile(
    r'\[([^\]]+)\](?:\[([^\]]*)\])?'
)

_AUTOLINK_RE = re.compile(
    r'<((?:https?|ftp)://[^>\s]+|[^>\s]+@[^>\s]+)>'
)

_DEFINITION_RE = re.compile(
    r'^\s{0,3}\[([^\]]+)\]:\s+(\S+)(?:\s+"[^"]*")?$'
)


def _is_skippable_url(url: str) -> bool:
    """검사하지 않는 URL 스킴/패턴."""
    if url.startswith(("mailto:", "data:", "javascript:", "tel:")):
        return True
    return bool(url.startswith("#"))


def _parse_definitions(lines: list[str]) -> dict[str, str]:
    """정의 테이블 [ref]: url 을 수집. ref_id 는 lower-cased."""
    defs: dict[str, str] = {}
    for line in lines:
        m = _DEFINITION_RE.match(line)
        if m:
            ref_id, url = m.group(1).lower(), m.group(2)
            defs[ref_id] = url
    return defs


def _strip_inline_code(line: str) -> str:
    """``code_fence.strip_inline_code`` 위임."""
    from md_doctor.extractors.code_fence import strip_inline_code
    return strip_inline_code(line)


def _emit_inline(
    refs: list[LinkRef],
    line: str,
    masked: str,
    line_no: int,
) -> None:
    """인라인 링크 매칭 → refs 추가."""
    for m in _INLINE_RE.finditer(masked):
        link_text, url = m.group(1), m.group(2)
        if _is_skippable_url(url):
            continue
        col = line.find("[", m.start())
        col = col + 1 if col >= 0 else m.start() + 1
        refs.append(
            LinkRef(target=url, line=line_no, col=col, text=link_text, kind="inline")
        )


def _emit_reference(
    refs: list[LinkRef],
    line: str,
    masked: str,
    line_no: int,
    definitions: dict[str, str],
) -> None:
    """참조/단축 링크 매칭 → refs 추가 (정의 테이블 기반)."""
    for m in _REFERENCE_RE.finditer(masked):
        link_text = m.group(1)
        ref_id_explicit = m.group(2)
        if ref_id_explicit is not None:
            ref_id = ref_id_explicit.lower()
            kind = "reference"
        else:
            ref_id = link_text.lower()
            kind = "shortcut"
        if ref_id not in definitions:
            continue
        url = definitions[ref_id]
        if _is_skippable_url(url):
            continue
        col = line.find("[", m.start())
        col = col + 1 if col >= 0 else m.start() + 1
        refs.append(
            LinkRef(target=url, line=line_no, col=col, text=link_text, kind=kind)
        )


def _emit_autolink(
    refs: list[LinkRef],
    line: str,
    masked: str,
    line_no: int,
) -> None:
    """자동 링크 매칭 → refs 추가."""
    for m in _AUTOLINK_RE.finditer(masked):
        url = m.group(1)
        if _is_skippable_url(url):
            continue
        col = line.find("<", m.start())
        col = col + 1 if col >= 0 else m.start() + 1
        refs.append(
            LinkRef(target=url, line=line_no, col=col, text="", kind="autolink")
        )


def _emit_definition(
    refs: list[LinkRef],
    line: str,
    line_no: int,
) -> None:
    """정의 자체 [ref]: url → kind=definition 으로 refs 추가."""
    m = _DEFINITION_RE.match(line)
    if m is None:
        return
    ref_id, url = m.group(1), m.group(2)
    if _is_skippable_url(url):
        return
    refs.append(
        LinkRef(
            target=url,
            line=line_no,
            col=m.start() + 1,
            text=ref_id,
            kind="definition",
        )
    )


def extract_link_refs(text: str, lines: list[str]) -> list[LinkRef]:
    """마크다운에서 모든 링크 참조를 추출.

    Parameters
    ----------
    text:
        원본 마크다운 텍스트.
    lines:
        ``text.splitlines()`` 와 동등한 줄 리스트.

    Returns
    -------
    list[LinkRef]
        인라인/참조/단축/자동 + 정의 (kind="definition"), 코드 영역 제외,
        skippable URL 제외.
    """
    definitions = _parse_definitions(lines)

    refs: list[LinkRef] = []
    in_code = False
    fence_marker: str | None = None

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_code:
                in_code = True
                fence_marker = marker
                continue
            elif fence_marker and stripped.startswith(fence_marker):
                in_code = False
                fence_marker = None
                continue
        if in_code:
            continue

        # 정의 라인 [ref]: url 은 본문 참조/단축 매칭에서 제외 (중복 방지)
        is_definition = bool(_DEFINITION_RE.match(line))
        _emit_definition(refs, line, i)
        if is_definition:
            continue

        masked = _strip_inline_code(line)
        _emit_inline(refs, line, masked, i)
        _emit_reference(refs, line, masked, i, definitions)
        _emit_autolink(refs, line, masked, i)

    return refs
