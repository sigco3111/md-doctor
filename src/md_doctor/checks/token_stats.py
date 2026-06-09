"""토큰 효율 통계 — LLM 입력용 메타데이터."""

from __future__ import annotations

import re
from typing import Any, Iterator

from md_doctor.checks import BaseCheck
from md_doctor.models import Diagnosis, Severity


class TokenStatsCheck(BaseCheck):
    """마크다운의 토큰 효율 통계를 INFO로 보고한다.

    0.1.0 에서는 단순 카운트(글자/단어/줄/리스트 밀도).
    0.2.0 에서 tiktoken 기반 정확한 토큰 카운트로 교체.
    """

    name = "token-stats"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        text: str = context["text"]
        lines: list[str] = context["lines"]
        char_count = len(text)
        # 단어: 한국어는 공백 기준, 영문/숫자는 \w+
        word_count = len(re.findall(r"\S+", text))
        line_count = len(lines)
        list_items = sum(1 for ln in lines if re.match(r"^\s*[-*+]\s", ln) or re.match(r"^\s*\d+\.\s", ln))
        code_lines = sum(1 for ln in lines if ln.lstrip().startswith("```") or ln.lstrip().startswith("    "))
        table_lines = sum(1 for ln in lines if ln.lstrip().startswith("|"))
        heading_lines = sum(1 for ln in lines if re.match(r"^#{1,6}\s", ln))

        msg = (
            f"chars={char_count:,} words={word_count:,} lines={line_count} "
            f"headings={heading_lines} lists={list_items} tables={table_lines} code={code_lines}"
        )
        yield Diagnosis(
            check=self.name,
            severity=Severity.INFO,
            message=msg,
            line=1,
            rule="TS001",
        )
