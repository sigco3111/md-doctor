"""extractors.links 단위 테스트 — 인라인/참조/자동 링크 + 코드 영역 스킵."""

from __future__ import annotations

from md_doctor.extractors.links import LinkRef, extract_link_refs


def test_extract_link_refs_inline():
    """인라인 링크: [text](url) → LinkRef 1개 (kind=inline)."""
    text = "[Site](https://example.com)"
    refs = extract_link_refs(text, text.splitlines())
    assert len(refs) == 1
    assert refs[0] == LinkRef(
        target="https://example.com", line=1, col=1, text="Site", kind="inline"
    )


def test_extract_link_refs_reference():
    """참조 링크: [text][ref] + [ref]: url."""
    text = "[Site][r]\n\n[r]: https://example.com"
    refs = extract_link_refs(text, text.splitlines())
    refs_only = [r for r in refs if r.kind != "definition"]
    assert len(refs_only) == 1
    assert refs_only[0].target == "https://example.com"
    assert refs_only[0].text == "Site"
    assert refs_only[0].kind == "reference"


def test_extract_link_refs_shortcut():
    """단축 참조: [ref] + [ref]: url (kind=shortcut)."""
    text = "[r]\n\n[r]: https://example.com"
    refs = extract_link_refs(text, text.splitlines())
    shortcuts = [r for r in refs if r.kind == "shortcut"]
    assert len(shortcuts) == 1
    assert shortcuts[0].target == "https://example.com"


def test_extract_link_refs_autolink():
    """자동 링크: <https://...> → kind=autolink."""
    text = "<https://example.com>"
    refs = extract_link_refs(text, text.splitlines())
    assert len(refs) == 1
    assert refs[0].kind == "autolink"
    assert refs[0].target == "https://example.com"


def test_extract_link_refs_ignores_code_fence():
    """코드펜스 내부 링크는 스킵."""
    text = "```\n[Site](https://missing.example.com)\n```\n"
    refs = extract_link_refs(text, text.splitlines())
    assert refs == []


def test_extract_link_refs_ignores_inline_code():
    """인라인 코드 내부 링크는 스킵."""
    text = "use `[a](b)` for examples"
    refs = extract_link_refs(text, text.splitlines())
    assert refs == []


def test_extract_link_refs_skips_mailto_data_javascript_fragment():
    """mailto:/data:/javascript:/fragment-only 는 스킵."""
    text = (
        "[m](mailto:foo@bar.com) "
        "[d](data:image/png;base64,abc) "
        "[j](javascript:void(0)) "
        "[f](#section)"
    )
    refs = extract_link_refs(text, text.splitlines())
    assert refs == []


def test_extract_link_refs_definition_not_target():
    """정의 자체는 kind=definition 으로 분류, 일반 참조와 구분."""
    text = "[r]: https://example.com"
    refs = extract_link_refs(text, text.splitlines())
    assert len(refs) == 1
    assert refs[0].kind == "definition"


def test_extract_link_refs_multiple_inline():
    """한 줄에 여러 인라인 링크."""
    text = "[A](https://a.com) and [B](https://b.com)"
    refs = extract_link_refs(text, text.splitlines())
    targets = {r.target for r in refs if r.kind == "inline"}
    assert targets == {"https://a.com", "https://b.com"}


def test_extract_link_refs_multiline():
    """여러 줄에 걸친 line 번호 정확."""
    text = "[A](https://a.com)\n\n[B](https://b.com)\n"
    refs = extract_link_refs(text, text.splitlines())
    assert [r.line for r in refs] == [1, 3]
