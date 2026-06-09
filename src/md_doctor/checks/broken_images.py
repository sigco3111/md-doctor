"""깨진 이미지 검사 — 로컬/원격 이미지 참조의 유효성 (0.2.0+ 예정)."""

from __future__ import annotations

from typing import Any, Iterator

from md_doctor.checks import BaseCheck
from md_doctor.models import Diagnosis


class BrokenImagesCheck(BaseCheck):
    """``![](...)`` 참조의 유효성 검사.

    0.1.0: 스텁. 기본 비활성.
    0.2.0+: 로컬은 Path.exists() / 원격은 HEAD 요청.
    """

    name = "broken-images"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        # TODO(0.2.0): ![](images/foo.png) 추출 → path.exists() 검사
        return iter(())
