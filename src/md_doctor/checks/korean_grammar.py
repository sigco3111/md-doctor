"""한국어 띄어쓰기/맞춤법 검사 — KS1~KS5 5개 규칙 (opt-in).

zero-deps, 정규식 기반. ``--korean`` 플래그 시에만 활성.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from md_doctor.checks import BaseCheck
from md_doctor.extractors.code_fence import (
    is_in_code_region,
    mark_code_regions,
    strip_inline_code,
)
from md_doctor.models import Diagnosis, Severity


_KS1_RE = re.compile(r"[A-Za-z]+(?=[가-힣])")
_KS2_RE = re.compile(r"[一-鿿㐀-䶿]+(?=[가-힣])")
_KS3_RE = re.compile(r"\d+\s+[가-힣]+")
_KS4_RE = re.compile(r" {2,}")
_KS5_RE = re.compile(r"\.{3,}")


def _has_inline_code(line: str) -> bool:
    """라인에 인라인 코드(`...`) 가 있는지 — 펜스 marker 자체는 제외.

    단순 ``"`" in line`` 은 펜스 marker (```` ``` ````) 도 매칭.
    인라인 코드는 `` `text` `` 처럼 백틱이 텍스트 사이에 있어야 함.
    """
    if "`" not in line:
        return False
    stripped = line.strip()
    # 펜스 marker 자체만 있는 라인은 인라인 코드 X
    if stripped.startswith("`") and stripped.strip("`") == "":
        return False
    if stripped.startswith("~") and stripped.strip("~") == "":
        return False
    return True


class KoreanGrammarCheck(BaseCheck):
    """한국어 띄어쓰기/맞춤법 검사 (KS1~KS5)."""

    name = "korean-grammar"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        lines: list[str] = context["lines"]
        fences = mark_code_regions(lines)
        for i, line in enumerate(lines, start=1):
            if is_in_code_region(i, fences):
                continue
            # 인라인 코드 영역은 strip 후 검사 (위치 보존).
            # 단, KS4 (중복 공백) 는 strip 결과가 아닌 원본 line 으로 검사 —
            # 인라인 코드 내부의 공백이 strip 후 연속 공백으로 보일 수 있음.
            has_inline = _has_inline_code(line)
            scan_line = strip_inline_code(line) if has_inline else line
            yield from self._ks1(scan_line, i)
            yield from self._ks2(scan_line, i)
            yield from self._ks3(scan_line, i)
            # KS4: 원본 line 으로 검사 (인라인 코드 보존된 공백 패턴)
            yield from self._ks4(line, i)
            yield from self._ks5(scan_line, i)

    @staticmethod
    def _ks1(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS1_RE.finditer(line):
            word = m.group(0)
            idx = m.end()
            next_char = line[idx] if idx < len(line) else ""
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message=f"영어 단어와 한글 사이 띄어쓰기 권장: '{word}{next_char}'",
                line=line_no,
                rule="KS1",
            )

    @staticmethod
    def _ks2(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS2_RE.finditer(line):
            word = m.group(0)
            idx = m.end()
            next_char = line[idx] if idx < len(line) else ""
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message=f"한자와 한글 사이 띄어쓰기 권장: '{word}{next_char}'",
                line=line_no,
                rule="KS2",
            )

    @staticmethod
    def _ks3(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS3_RE.finditer(line):
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.WARNING,
                message=f"숫자와 한글 단위 사이 띄어쓰기 없음: '{m.group(0).strip()}'",
                line=line_no,
                rule="KS3",
            )

    @staticmethod
    def _ks4(line: str, line_no: int) -> Iterator[Diagnosis]:
        if _KS4_RE.search(line):
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message="중복 공백 발견",
                line=line_no,
                rule="KS4",
            )

    @staticmethod
    def _ks5(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS5_RE.finditer(line):
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message="'...' 대신 '…' 권장",
                line=line_no,
                rule="KS5",
            )

    @staticmethod
    def _ks1(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS1_RE.finditer(line):
            word = m.group(0)
            idx = m.end()
            next_char = line[idx] if idx < len(line) else ""
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message=f"영어 단어와 한글 사이 띄어쓰기 권장: '{word}{next_char}'",
                line=line_no,
                rule="KS1",
            )

    @staticmethod
    def _ks2(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS2_RE.finditer(line):
            word = m.group(0)
            idx = m.end()
            next_char = line[idx] if idx < len(line) else ""
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message=f"한자와 한글 사이 띄어쓰기 권장: '{word}{next_char}'",
                line=line_no,
                rule="KS2",
            )

    @staticmethod
    def _ks3(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS3_RE.finditer(line):
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.WARNING,
                message=f"숫자와 한글 단위 사이 띄어쓰기 없음: '{m.group(0).strip()}'",
                line=line_no,
                rule="KS3",
            )

    @staticmethod
    def _ks4(line: str, line_no: int) -> Iterator[Diagnosis]:
        if _KS4_RE.search(line):
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message="중복 공백 발견",
                line=line_no,
                rule="KS4",
            )

    @staticmethod
    def _ks5(line: str, line_no: int) -> Iterator[Diagnosis]:
        for m in _KS5_RE.finditer(line):
            yield Diagnosis(
                check="korean-grammar",
                severity=Severity.INFO,
                message="'...' 대신 '…' 권장",
                line=line_no,
                rule="KS5",
            )
