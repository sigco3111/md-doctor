"""extractors.html 단위 테스트."""

from __future__ import annotations

from md_doctor.extractors.code_fence import mark_code_regions
from md_doctor.extractors.html import HtmlRef, extract_html_refs


def test_extract_html_refs_self_closing_img():
    """<img src="x.png" alt="foo" /> 추출."""
    text = '<img src="x.png" alt="foo" />'
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert len(refs) == 1
    assert refs[0].tag == "img"
    assert refs[0].attrs["src"] == "x.png"
    assert refs[0].attrs["alt"] == "foo"
    assert refs[0].kind == "inline"


def test_extract_html_refs_paired_anchor():
    """<a href="x.md">text</a> 추출."""
    text = '<a href="x.md">click</a>'
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert len(refs) == 1
    assert refs[0].tag == "a"
    assert refs[0].attrs["href"] == "x.md"


def test_extract_html_refs_block_div():
    """<div>content</div> 추출 (kind=block)."""
    text = "<div>hello</div>"
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert len(refs) == 1
    assert refs[0].tag == "div"
    assert refs[0].kind == "block"


def test_extract_html_refs_br():
    """<br> 추출."""
    text = "line<br>break"
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert len(refs) == 1
    assert refs[0].tag == "br"


def test_extract_html_refs_ignores_code_fence():
    """코드펜스 내부 HTML 무시."""
    text = '```\n<img src="x.png">\n```\n'
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert refs == []


def test_extract_html_refs_ignores_inline_code():
    """인라인 코드 내부 HTML 무시."""
    text = 'use `<img src="x">` for examples'
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert refs == []


def test_extract_html_refs_multiple():
    """여러 태그 추출."""
    text = '<img src="a.png"> <a href="b.md">b</a> <div>x</div>'
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert len(refs) == 3
    assert {r.tag for r in refs} == {"img", "a", "div"}


def test_extract_html_refs_line_col():
    """line, col 정확."""
    text = 'para\n<img src="x.png">\n'
    lines = text.splitlines()
    refs = extract_html_refs(text, lines, mark_code_regions(lines))
    assert len(refs) == 1
    assert refs[0].line == 2
    assert refs[0].col == 1
