"""마크다운 추출기 — 텍스트에서 의미 단위(이미지/링크/표 등)를 추출.

이 모듈의 함수는 **순수** — 부수효과 없음, 디스크/네트워크 미사용.
체크 모듈은 추출기 결과를 받아 진단으로 변환한다.
"""

from md_doctor.extractors.images import ImageRef, extract_image_refs

__all__ = [
    "ImageRef",
    "extract_image_refs",
]
