"""검사 모듈 베이스 + 레지스트리.

이 모듈은 ``models`` 만 직접 의존 (체크 서브모듈은 함수 호출 시 lazy import).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterator, Sequence, Type

from md_doctor.models import Diagnosis, Severity


class BaseCheck(ABC):
    """모든 검사 모듈의 베이스.

    서브클래스는 ``name`` 과 ``run()`` 만 구현하면 된다.
    """

    #: 사람이 읽을 검사 이름 (e.g. "dead-links")
    name: str = ""

    @abstractmethod
    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        """context는 다음 키들을 가진다:

        - ``text``: 전체 마크다운 텍스트
        - ``lines``: 줄 단위 리스트
        - ``path``: ``pathlib.Path``
        """
        ...


@dataclass
class CheckRegistry:
    """검사 모듈 묶음. 등록된 순서대로 실행된다."""

    checks: list[BaseCheck]

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        for check in self.checks:
            yield from check.run(context)

    @classmethod
    def from_classes(cls, classes: Sequence[Type[BaseCheck]]) -> "CheckRegistry":
        return cls(checks=[c() for c in classes])

    def names(self) -> list[str]:
        return [c.name for c in self.checks]


def default_checks() -> CheckRegistry:
    """기본 검사 세트를 반환한다.

    0.1.0: 토큰 통계(항상 INFO) + 헤딩 일관성만 활성화.
    나머지 체크는 0.2.0+ 에서 차례로 활성화.
    """
    from md_doctor.checks.broken_images import BrokenImagesCheck
    from md_doctor.checks.dead_links import DeadLinksCheck
    from md_doctor.checks.heading_consistency import HeadingConsistencyCheck
    from md_doctor.checks.token_stats import TokenStatsCheck

    return CheckRegistry(
        checks=[
            TokenStatsCheck(),
            HeadingConsistencyCheck(),
            # 0.2.0+ 예정 (스텁은 만들어 두되 기본 비활성)
            # DeadLinksCheck(),
            # BrokenImagesCheck(),
        ]
    )


__all__ = [
    "BaseCheck",
    "CheckRegistry",
    "default_checks",
    "Severity",
    "Diagnosis",
]
