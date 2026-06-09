"""이미지 참조 추출기 — 마크다운 본문에서 `![](...)` 형태를 파싱.

순수 함수. 부수효과 없음. 디스크/네트워크 미사용.
- 코드펜스(```/~~~) 내부 제외
- 인라인 코드(`...`) 내부 제외
- 원격 URL (http://, https://, mailto:, data:) 제외
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ImageRef:
    """마크다운에서 추출한 단일 이미지 참조."""

    target: str
    line: int
    col: int
    alt: str = ""


# ![alt](url "title") 패턴
_IMAGE_RE = re.compile(
    r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
)


def extract_image_refs(
    text: str,
    lines: list[str],
) -> list[ImageRef]:
    """마크다운에서 `![](...)` / `![alt](...)` 참조를 추출.

    Parameters
    ----------
    text:
        원본 마크다운 텍스트.
    lines:
        ``text.splitlines()`` 와 동등한 줄 리스트.

    Returns
    -------
    list[ImageRef]
        코드펜스 / 인라인 코드 외부, 원격 URL / data: URL 제외한 참조.
    """
    refs: list[ImageRef] = []
    in_code = False
    fence_marker: str | None = None

    for i, line in enumerate(lines, start=1):
        # 1단계: 코드펜스 토글
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_code:
                in_code = True
                fence_marker = marker
                continue  # 펜스 시작 줄 자체는 스킵
            elif fence_marker and stripped.startswith(fence_marker):
                in_code = False
                fence_marker = None
                continue  # 펜스 끝 줄 자체는 스킵
        if in_code:
            continue

        # 2단계: 인라인 코드 영역 마스킹 후 매칭
        masked = _strip_inline_code(line)
        for m in _IMAGE_RE.finditer(masked):
            alt = m.group(1)
            target = m.group(2)
            if target.startswith(("http://", "https://", "data:", "mailto:")):
                continue
            # col 은 원본 line 기준 위치 (마스킹 후 변할 수 있으므로 원본에서 재탐색)
            col = line.find("![", m.start())
            if col < 0:
                col = m.start() + 1
            else:
                col += 1  # 1-based
            refs.append(ImageRef(target=target, line=i, col=col, alt=alt))
    return refs


def _strip_inline_code(line: str) -> str:
    """인라인 코드(`...`) 영역을 공백으로 치환 (위치 보존).

    코드 외부의 `![...](...)` 매칭은 그대로 유지.
    """
    out: list[str] = []
    in_code = False
    for ch in line:
        if ch == "`":
            in_code = not in_code
            out.append(" ")  # 백틱 자체를 공백으로
        elif in_code:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)
