"""extractors.code_fence 단위 테스트."""

from __future__ import annotations

from md_doctor.extractors.code_fence import (
    CodeFence,
    is_in_code_region,
    mark_code_regions,
    strip_inline_code,
)


def test_mark_code_regions_no_fence():
    """코드펜스 없음 → 빈 리스트."""
    lines = ["hello", "world"]
    fences = mark_code_regions(lines)
    assert fences == []


def test_mark_code_regions_simple_fence():
    """단순 펜스 1개."""
    lines = ["```python", "print()", "```"]
    fences = mark_code_regions(lines)
    assert len(fences) == 1
    assert fences[0] == CodeFence(start_line=1, end_line=3, language="python", marker="```")


def test_mark_code_regions_tilde_fence():
    """~~~ 펜스."""
    lines = ["~~~bash", "echo hi", "~~~"]
    fences = mark_code_regions(lines)
    assert len(fences) == 1
    assert fences[0].marker == "~~~"


def test_mark_code_regions_unclosed():
    """미닫힌 펜스 → end_line=None."""
    lines = ["```", "code", "more"]
    fences = mark_code_regions(lines)
    assert len(fences) == 1
    assert fences[0].end_line is None


def test_is_in_code_region():
    """특정 줄이 코드 영역 내부인지."""
    lines = ["a", "```", "b", "```", "c"]
    fences = mark_code_regions(lines)
    assert is_in_code_region(1, fences) is False
    assert is_in_code_region(2, fences) is False  # fence 시작 자체
    assert is_in_code_region(3, fences) is True
    assert is_in_code_region(4, fences) is False  # fence 끝 자체
    assert is_in_code_region(5, fences) is False


def test_strip_inline_code_preserves_position():
    """인라인 코드 영역을 공백으로 치환, 위치 보존."""
    line = "a `code` b"
    result = strip_inline_code(line)
    assert result == "a       b"
    assert len(result) == len(line)
