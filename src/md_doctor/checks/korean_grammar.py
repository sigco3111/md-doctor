"""한국어 띄어쓰기/맞춤법 검사 — KS1~KS5 5개 규칙 (opt-in).

zero-deps, 정규식 기반. ``--korean`` 플래그 시에만 활성.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from md_doctor.checks import BaseCheck
from md_doctor.extractors.code_fence import is_in_code_region, mark_code_regions
from md_doctor.models import Diagnosis, Severity


_KS1_RE = re.compile(r"[A-Za-z]+(?=[가-힣])")
_KS2_RE = re.compile(r"[一-鿿㐀-䶿]+(?=[가-힣])")
_KS3_RE = re.compile(r"\d+\s+[가-힣]+")
_KS4_RE = re.compile(r" {2,}")
_KS5_RE = re.compile(r"\.{3,}")


class KoreanGrammarCheck(BaseCheck):
    """한국어 띄어쓰기/맞춤법 검사 (KS1~KS5)."""

    name = "korean-grammar"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        lines: list[str] = context["lines"]
        fences = mark_code_regions(lines)
        for i, line in enumerate(lines, start=1):
            if is_in_code_region(i, fences):
                continue
            yield from self._ks1(line, i)
            yield from self._ks2(line, i)
            yield from self._ks3(line, i)
            yield from self._ks4(line, i)
            yield from self._ks5(line, i)

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
