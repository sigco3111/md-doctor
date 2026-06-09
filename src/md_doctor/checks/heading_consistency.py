"""헤딩 일관성 검사 — 제목-첫-헤딩 / 한↔영 혼용 / 단계 패턴."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterator

from md_doctor.checks import BaseCheck
from md_doctor.models import Diagnosis, Severity


# 코드블록 내부를 무시하기 위한 단순 토크나이저
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})", re.MULTILINE)


class HeadingConsistencyCheck(BaseCheck):
    """H1 단일 / 제목-첫-헤딩 일치 / 단계 헤딩 규칙 검사."""

    name = "heading-consistency"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        text: str = context["text"]
        lines: list[str] = context["lines"]
        path: Path = context["path"]

        body = _strip_code_fences(text)
        headings = self._extract_headings(body, lines)

        # HC001: H1이 2개 이상이면 경고
        h1s = [h for h in headings if h["level"] == 1]
        if len(h1s) > 1:
            yield Diagnosis(
                check=self.name,
                severity=Severity.WARNING,
                message=f"H1 헤딩이 {len(h1s)}개입니다 (권장: 1개).",
                line=h1s[1]["line"],
                rule="HC001",
            )

        # HC002: 파일명(확장자 제외) ↔ 첫 H1 일치 검사
        if h1s:
            first_h1 = h1s[0]["text"]
            stem = path.stem.replace("-", " ").replace("_", " ")
            if stem and first_h1 and not self._loose_match(stem, first_h1):
                yield Diagnosis(
                    check=self.name,
                    severity=Severity.INFO,
                    message=(
                        f"파일명 '{path.stem}' 과 첫 H1 '{first_h1}' 이 다릅니다. "
                        "SEO/탐색 친화적 일치를 권장합니다."
                    ),
                    line=h1s[0]["line"],
                    rule="HC002",
                )

        # HC003: 단계 헤딩이 1, 2, 3, ... 순서로 증가하는지
        step_pattern = re.compile(r"^(\d+)\.\s")
        prev_step = 0
        for h in headings:
            m = step_pattern.match(h["text"])
            if m:
                cur = int(m.group(1))
                if prev_step and cur != prev_step + 1:
                    yield Diagnosis(
                        check=self.name,
                        severity=Severity.INFO,
                        message=(
                            f"단계 헤딩 점프: {prev_step} → {cur} "
                            "(1씩 증가 권장)."
                        ),
                        line=h["line"],
                        rule="HC003",
                    )
                prev_step = cur

        # HC004: 빈 헤딩
        for h in headings:
            if not h["text"].strip():
                yield Diagnosis(
                    check=self.name,
                    severity=Severity.WARNING,
                    message="빈 헤딩입니다.",
                    line=h["line"],
                    rule="HC004",
                )

    @staticmethod
    def _extract_headings(body: str, lines: list[str]) -> list[dict[str, Any]]:
        """코드펜스 제거된 본문에서 헤딩 추출."""
        # 줄 단위 매칭이 더 안전 — 원본 line 번호 보존
        result: list[dict[str, Any]] = []
        in_code = False
        fence_marker: str | None = None
        for i, raw in enumerate(lines, start=1):
            stripped = raw.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                marker = stripped[:3]
                if not in_code:
                    in_code = True
                    fence_marker = marker
                elif fence_marker and stripped.startswith(fence_marker):
                    in_code = False
                    fence_marker = None
                continue
            if in_code:
                continue
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", raw)
            if m:
                result.append({"level": len(m.group(1)), "text": m.group(2).strip(), "line": i})
        return result

    @staticmethod
    def _loose_match(a: str, b: str) -> bool:
        """공백/대소문자/구두점 무시 비교."""
        norm = lambda s: re.sub(r"[\s\W_]+", "", s.lower())  # noqa: E731
        return norm(a) == norm(b)


def _strip_code_fences(text: str) -> str:
    """코드펜스 영역을 공백으로 치환 (라인 보존)."""
    out_lines: list[str] = []
    in_code = False
    fence_marker: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_code:
                in_code = True
                fence_marker = marker
                out_lines.append("")  # 헤더 라인만 제거
            elif fence_marker and stripped.startswith(fence_marker):
                in_code = False
                fence_marker = None
                out_lines.append("")  # 닫는 라인만 제거
            else:
                out_lines.append(line)
        elif in_code:
            out_lines.append("")  # 코드 내용 제거
        else:
            out_lines.append(line)
    return "\n".join(out_lines)
