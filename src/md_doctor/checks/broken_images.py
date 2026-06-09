"""깨진 이미지 검사 — 로컬 이미지 참조의 유효성.

원격 URL (http://, https://, data:, mailto:) 은 스킵 (dead-links 의 범위).
HTML ``<img src>`` 는 0.3.0+ 에서 다룸 (YAGNI).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from md_doctor.checks import BaseCheck
from md_doctor.extractors.images import extract_image_refs
from md_doctor.models import Diagnosis, Severity


class BrokenImagesCheck(BaseCheck):
    """`![](...)` 참조의 로컬 파일 유효성 검사."""

    name = "broken-images"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        path: Path = context["path"]
        base_dir = path.parent
        refs = extract_image_refs(context["text"], context["lines"])

        for ref in refs:
            try:
                target = _resolve_path(base_dir, ref.target)
            except (ValueError, OSError) as e:
                yield Diagnosis(
                    check=self.name,
                    severity=Severity.ERROR,
                    message=(
                        f"깨진 이미지 참조: 경로 해석 실패 '{ref.target}': {e}"
                    ),
                    line=ref.line,
                    rule="BI001",
                )
                continue

            if not target.exists():
                yield Diagnosis(
                    check=self.name,
                    severity=Severity.ERROR,
                    message=(
                        f"깨진 이미지 참조: '{ref.target}' (해상: {target})"
                    ),
                    line=ref.line,
                    rule="BI001",
                )
                continue

            if target.is_dir():
                yield Diagnosis(
                    check=self.name,
                    severity=Severity.ERROR,
                    message=(
                        f"깨진 이미지 참조: '{ref.target}' 은(는) "
                        "디렉터리입니다 (파일이어야 함)"
                    ),
                    line=ref.line,
                    rule="BI001",
                )


def _resolve_path(base_dir: Path, target: str) -> Path:
    """base_dir 기준 상대경로 해석. 절대 경로는 그대로.

    ``Path.resolve()`` 로 ``../`` 를 정규화하여 메시지에 깔끔한 절대 경로 표시.
    """
    p = Path(target)
    if p.is_absolute():
        return p
    return (base_dir / p).resolve()
