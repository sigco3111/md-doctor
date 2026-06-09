"""데드 링크 검사 — 마크다운 본문/이미지 URL의 HEAD 요청 (0.2.0+ 예정)."""

from __future__ import annotations

from typing import Any, Iterator

from md_doctor.checks import BaseCheck
from md_doctor.models import Diagnosis


class DeadLinksCheck(BaseCheck):
    """외부/내부 링크가 살아있는지 확인.

    0.1.0: 스텁. 기본 비활성.
    0.2.0+: HEAD 요청 + 병렬 처리 + 캐시.
    """

    name = "dead-links"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        # TODO(0.2.0): URL 추출 → HEAD 요청 → 4xx/5xx 분류
        # 로컬 파일 경로면 Path.exists() 로 검사 (이미지 모듈과 중복 가능)
        return iter(())
