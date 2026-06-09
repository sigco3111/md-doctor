"""extractors.images 단위 테스트 — 정규식 매칭과 코드 영역 스킵 검증."""

from __future__ import annotations

from md_doctor.extractors.images import ImageRef, extract_image_refs


def test_extract_image_refs_basic():
    """기본: ![](x.png) → ImageRef 1개, line=1, col=1."""
    text = "![](x.png)"
    refs = extract_image_refs(text, text.splitlines())
    assert len(refs) == 1
    assert refs[0] == ImageRef(target="x.png", line=1, col=1, alt="")


def test_extract_image_refs_with_alt():
    """alt 텍스트 보존."""
    text = "![My Alt](x.png)"
    refs = extract_image_refs(text, text.splitlines())
    assert len(refs) == 1
    assert refs[0].alt == "My Alt"
    assert refs[0].target == "x.png"


def test_extract_image_refs_ignores_link_without_bang():
    """`[](url)` (느낌표 없음) 은 이미지가 아님 — 스킵."""
    text = "[not image](x.png)"
    refs = extract_image_refs(text, text.splitlines())
    assert refs == []


def test_extract_image_refs_skips_remote_url():
    """http(s):// URL 은 스킵."""
    text = "![Remote](https://example.com/x.png)"
    refs = extract_image_refs(text, text.splitlines())
    assert refs == []


def test_extract_image_refs_skips_data_url():
    """data: URL 은 스킵."""
    text = "![Inline](data:image/png;base64,abc)"
    refs = extract_image_refs(text, text.splitlines())
    assert refs == []


def test_extract_image_refs_skips_mailto():
    """mailto: URL 은 스킵."""
    text = "![Mail](mailto:foo@bar.com)"
    refs = extract_image_refs(text, text.splitlines())
    assert refs == []


def test_extract_image_refs_ignores_code_fence():
    """``` ``` ``` 코드펜스 내부 ![](...) 는 스킵."""
    text = "```\n![](missing.png)\n```\n"
    refs = extract_image_refs(text, text.splitlines())
    assert refs == []


def test_extract_image_refs_ignores_inline_code():
    """인라인 코드(`` `...` ``) 내부 ![](...) 는 스킵."""
    text = "use `![](missing.png)` for docs"
    refs = extract_image_refs(text, text.splitlines())
    assert refs == []


def test_extract_image_refs_handles_title():
    """`![alt](url \"title\")` 의 title 은 무시, target 만 추출."""
    text = '![A](x.png "Title here")'
    refs = extract_image_refs(text, text.splitlines())
    assert len(refs) == 1
    assert refs[0].target == "x.png"
    assert refs[0].alt == "A"


def test_extract_image_refs_multiple_per_line():
    """한 줄에 여러 이미지 — 모두 추출."""
    text = "![A](a.png) and ![B](b.png)"
    refs = extract_image_refs(text, text.splitlines())
    assert len(refs) == 2
    assert {r.target for r in refs} == {"a.png", "b.png"}


def test_extract_image_refs_multiline():
    """여러 줄에 걸친 추출, line 번호 정확."""
    text = "![A](a.png)\n\n![B](b.png)\n"
    refs = extract_image_refs(text, text.splitlines())
    assert [r.line for r in refs] == [1, 3]
