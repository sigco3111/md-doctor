"""코드펜스 + 인라인 코드 마킹 — 추출기 공통 헬퍼.

순수 함수. 부수효과 없음.
- ``CodeFence``: 펜스 한 구간 (시작/끝/언어/마커)
- ``mark_code_regions(lines)``: 모든 펜스 구간 찾기
- ``is_in_code_region(line_no, fences)``: 특정 줄이 코드 내부인지
- ``strip_inline_code(line)``: 인라인 코드 영역을 공백으로 (위치 보존)
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CodeFence:
    """코드펜스 한 구간."""

    start_line: int
    end_line: int | None
    language: str = ""
    marker: str = "```"


_FENCE_OPEN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def mark_code_regions(lines: list[str]) -> list[CodeFence]:
    """모든 코드펜스 구간을 list[CodeFence] 로 반환."""
    fences: list[CodeFence] = []
    in_code = False
    open_fence: CodeFence | None = None
    open_marker: str | None = None

    for i, line in enumerate(lines, start=1):
        m = _FENCE_OPEN_RE.match(line)
        if m:
            marker = m.group(2)[:3]
            if not in_code:
                language = m.group(3).strip().split()[0] if m.group(3).strip() else ""
                open_fence = CodeFence(
                    start_line=i, end_line=None, language=language, marker=marker
                )
                in_code = True
                open_marker = marker
            elif open_marker and line.lstrip().startswith(open_marker):
                if open_fence is not None:
                    fences.append(
                        CodeFence(
                            start_line=open_fence.start_line,
                            end_line=i,
                            language=open_fence.language,
                            marker=open_fence.marker,
                        )
                    )
                in_code = False
                open_fence = None
                open_marker = None

    if open_fence is not None:
        fences.append(open_fence)

    return fences


def is_in_code_region(line_no: int, fences: list[CodeFence]) -> bool:
    """주어진 줄 번호가 어떤 코드펜스 내부인지."""
    for f in fences:
        if f.end_line is None:
            if line_no > f.start_line:
                return True
        else:
            if f.start_line < line_no < f.end_line:
                return True
    return False


def strip_inline_code(line: str) -> str:
    """인라인 코드(`...`) 영역을 공백으로 치환 (위치 보존).

    코드 외부의 `![...](...)` 또는 `[...](...)` 매칭은 그대로 유지.
    """
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
