"""깨진 이미지 검사 — 로컬 이미지 참조의 유효성.

원격 URL (http://, https://, data:, mailto:) 은 스킵 (dead-links 의 범위).
HTML ``<img src>`` 는 v0.3.0+ 에서 처리.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from md_doctor.checks import BaseCheck
from md_doctor.extractors.code_fence import mark_code_regions
from md_doctor.extractors.html import extract_html_refs
from md_doctor.extractors.images import ImageRef, extract_image_refs
from md_doctor.models import Diagnosis, Severity


class BrokenImagesCheck(BaseCheck):
    """`![](...)` / `<img src>` 참조의 로컬 파일 유효성 검사."""

    name = "broken-images"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        path: Path = context["path"]
        base_dir = path.parent
        fences = mark_code_regions(context["lines"])

        # 1. 마크다운 ![](...)
        for ref in extract_image_refs(context["text"], context["lines"]):
            yield from self._process_ref(base_dir, ref, rule="BI001")

        # 2. HTML <img src>
        for ref in self._html_to_image_refs(
            extract_html_refs(context["text"], context["lines"], fences)
        ):
            yield from self._process_ref(base_dir, ref, rule="BI002")

    @staticmethod
    def _html_to_image_refs(html_refs) -> Iterator[ImageRef]:
        """HtmlRef(tag='img') → ImageRef 변환."""
        for ref in html_refs:
            if ref.tag == "img" and "src" in ref.attrs:
                yield ImageRef(
                    target=ref.attrs["src"],
                    line=ref.line,
                    col=ref.col,
                    alt=ref.attrs.get("alt", ""),
                )

    @staticmethod
    def _process_ref(
        base_dir: Path, ref: ImageRef, *, rule: str
    ) -> Iterator[Diagnosis]:
        try:
            target = _resolve_path(base_dir, ref.target)
        except (ValueError, OSError) as e:
            yield Diagnosis(
                check="broken-images",
                severity=Severity.ERROR,
                message=f"깨진 이미지 참조: 경로 해석 실패 '{ref.target}': {e}",
                line=ref.line,
                rule=rule,
            )
            return

        if not target.exists():
            yield Diagnosis(
                check="broken-images",
                severity=Severity.ERROR,
                message=f"깨진 이미지 참조: '{ref.target}' (해상: {target})",
                line=ref.line,
                rule=rule,
            )
            return

        if target.is_dir():
            yield Diagnosis(
                check="broken-images",
                severity=Severity.ERROR,
                message=(
                    f"깨진 이미지 참조: '{ref.target}' 은(는) 디렉터리입니다"
                ),
                line=ref.line,
                rule=rule,
            )


def _resolve_path(base_dir: Path, target: str) -> Path:
    """base_dir 기준 상대경로 해석. 절대 경로는 그대로.

    ``Path.resolve()`` 로 ``../`` 를 정규화하여 메시지에 깔끔한 절대 경로 표시.
    """
    p = Path(target)
    if p.is_absolute():
        return p
    return (base_dir / p).resolve()
