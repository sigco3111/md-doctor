"""GFM/CommonMark 규칙 린트 — HC005~008 4개 규칙 단일 체크."""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from md_doctor.checks import BaseCheck
from md_doctor.extractors.code_fence import CodeFence, mark_code_regions
from md_doctor.extractors.html import extract_html_refs
from md_doctor.models import Diagnosis, Severity


# GFM-호환 HTML (HC007 면제)
_GFM_ALLOWED_HTML = frozenset({"br", "kbd", "sub", "sup", "details", "summary"})

# 리스트 글머리: - * +
_BULLET_RE = re.compile(r"^(\s*)([-*+])(\s|$)")
# 순서 리스트: 1. or 1)
_ORDERED_RE = re.compile(r"^(\s*)(\d+)([.)])(\s|$)")

# 테이블 separator: |---|:---:| 등
_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")


class GfmLintCheck(BaseCheck):
    """GFM/CommonMark 규칙 린트."""

    name = "gfm-lint"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        text: str = context["text"]
        lines: list[str] = context["lines"]
        fences = mark_code_regions(lines)

        yield from _check_hc005(lines, fences)
        yield from _check_hc006(fences)
        yield from _check_hc007(text, lines, fences)
        yield from _check_hc008(lines, fences)


def _check_hc005(lines, fences) -> Iterator[Diagnosis]:
    """HC005: 리스트 점 패턴 일관성."""
    bullets: set[str] = set()
    ordered_marks: set[str] = set()

    for i, line in enumerate(lines, start=1):
        if _is_in_fence(i, fences):
            continue
        m_b = _BULLET_RE.match(line)
        m_o = _ORDERED_RE.match(line)
        if m_b:
            bullets.add(m_b.group(2))
        if m_o:
            ordered_marks.add(m_o.group(3))

    if len(bullets) > 1:
        yield Diagnosis(
            check="gfm-lint",
            severity=Severity.WARNING,
            message=(
                f"글머리 기호 혼용: {sorted(bullets)}. "
                "하나만 사용 권장."
            ),
            rule="HC005",
        )
    if len(ordered_marks) > 1:
        yield Diagnosis(
            check="gfm-lint",
            severity=Severity.WARNING,
            message=(
                f"순서 리스트 마커 혼용: {sorted(ordered_marks)}. "
                "하나만 사용 권장."
            ),
            rule="HC005",
        )


def _check_hc006(fences) -> Iterator[Diagnosis]:
    """HC006: 코드언어 미지정."""
    for fence in fences:
        if fence.end_line is not None and not fence.language:
            yield Diagnosis(
                check="gfm-lint",
                severity=Severity.INFO,
                message=(
                    f"코드언어 미지정 (라인 {fence.start_line}). "
                    "신택스 하이라이팅 개선을 위해 ```언어 지정 권장."
                ),
                line=fence.start_line,
                rule="HC006",
            )


def _check_hc007(text, lines, fences) -> Iterator[Diagnosis]:
    """HC007: raw HTML 사용."""
    for ref in extract_html_refs(text, lines, fences):
        if ref.tag in _GFM_ALLOWED_HTML:
            continue
        yield Diagnosis(
            check="gfm-lint",
            severity=Severity.WARNING,
            message=(
                f"raw HTML <{ref.tag}> 사용 (라인 {ref.line}). "
                "마크다운 대체 권장 (호환성)."
            ),
            line=ref.line,
            rule="HC007",
        )


def _check_hc008(lines, fences) -> Iterator[Diagnosis]:
    """HC008: 테이블 정렬."""
    for i, line in enumerate(lines, start=1):
        if _is_in_fence(i, fences):
            continue
        if not _SEPARATOR_RE.match(line):
            continue
        if i < 2:
            continue
        header_line = lines[i - 2]
        n_header = _count_table_columns(header_line)
        n_sep = _count_table_columns(line)
        if n_header != n_sep:
            yield Diagnosis(
                check="gfm-lint",
                severity=Severity.WARNING,
                message=(
                    f"테이블 정렬 불일치 (라인 {i}): "
                    f"헤더 {n_header}열 vs separator {n_sep}열."
                ),
                line=i,
                rule="HC008",
            )


def _is_in_fence(line_no: int, fences: list[CodeFence]) -> bool:
    """펜스 시작/끝 자체는 검사 대상 (라인이 펜스 boundary 면 스킵)."""
    for f in fences:
        if f.end_line is None:
            if line_no >= f.start_line:
                return True
        else:
            if f.start_line <= line_no <= f.end_line:
                return True
    return False


def _count_table_columns(row: str) -> int:
    """테이블 행의 열 개수 계산."""
    row = row.strip()
    if not row or set(row) <= {"|", " "}:
        return 0
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return len([c for c in row.split("|") if c.strip()])
