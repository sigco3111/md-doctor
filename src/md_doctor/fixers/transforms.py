"""자동 후처리 변환 — 6개 안전한 변형.

F1~F6 순서로 적용 (BOM 우선, CRLF 마지막).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FixResult:
    """fix 1회의 결과."""

    original: str
    fixed: str
    changes: list[str] = field(default_factory=list)
    changed_lines: list[int] = field(default_factory=list)


def f1_trailing_newline(text: str) -> tuple[str, bool]:
    """F1: 파일 끝 newline 1개 보장."""
    if not text or text.endswith("\n"):
        return text, False
    return text + "\n", True


def f2_trailing_whitespace(text: str) -> tuple[str, bool]:
    """F2: 라인 끝 공백 제거."""
    lines = text.split("\n")
    new_lines = [line.rstrip() for line in lines]
    new_text = "\n".join(new_lines)
    return new_text, new_text != text


def f3_heading_blank_line(text: str) -> tuple[str, bool]:
    """F3: H1/H2 헤딩 다음 빈 줄 보장."""
    lines = text.split("\n")
    new_lines: list[str] = []
    heading_re = re.compile(r"^#{1,2}\s+\S")
    changed = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        if (
            heading_re.match(line)
            and i + 1 < len(lines)
            and lines[i + 1].strip() != ""
        ):
            new_lines.append("")
            changed = True
    new_text = "\n".join(new_lines)
    return new_text, changed


def f4_empty_heading(text: str) -> tuple[str, bool]:
    """F4: 빈 헤딩 제거."""
    lines = text.split("\n")
    empty_re = re.compile(r"^#{1,6}\s*$")
    new_lines = [line for line in lines if not empty_re.match(line)]
    new_text = "\n".join(new_lines)
    return new_text, new_text != text


def f5_strip_bom(text: str) -> tuple[str, bool]:
    """F5: UTF-8 BOM 제거."""
    if text.startswith("\ufeff"):
        return text[1:], True
    return text, False


def f6_crlf_to_lf(text: str) -> tuple[str, bool]:
    """F6: CRLF → LF."""
    if "\r\n" in text:
        return text.replace("\r\n", "\n"), True
    return text, False


ALL_TRANSFORMS: list[tuple[str, Callable[[str], tuple[str, bool]]]] = [
    ("F5", f5_strip_bom),
    ("F6", f6_crlf_to_lf),
    ("F1", f1_trailing_newline),
    ("F2", f2_trailing_whitespace),
    ("F3", f3_heading_blank_line),
    ("F4", f4_empty_heading),
]


def _track_changed_lines(
    before: str, after: str, changed: set[int]
) -> None:
    """변경된 라인 추적 (간이: splitlines 비교)."""
    before_lines = before.split("\n")
    after_lines = after.split("\n")
    n = max(len(before_lines), len(after_lines))
    for i in range(n):
        b = before_lines[i] if i < len(before_lines) else None
        a = after_lines[i] if i < len(after_lines) else None
        if b != a:
            changed.add(i + 1)


def apply_fixes(
    text: str,
    *,
    enabled: set[str] | None = None,
) -> FixResult:
    """모든 enabled 변환을 순서대로 적용.

    enabled: None = 모두 적용. set 으로 활성화 subset 지정 가능.
    """
    enabled_ids = enabled or {fid for fid, _ in ALL_TRANSFORMS}
    current = text
    applied: list[str] = []
    changed_lines: set[int] = set()

    for fid, transform in ALL_TRANSFORMS:
        if fid not in enabled_ids:
            continue
        new_text, changed = transform(current)
        if changed:
            _track_changed_lines(current, new_text, changed_lines)
            applied.append(fid)
        current = new_text

    return FixResult(
        original=text,
        fixed=current,
        changes=applied,
        changed_lines=sorted(changed_lines),
    )
