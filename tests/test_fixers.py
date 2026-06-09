"""fixers.transforms 단위 테스트."""

from __future__ import annotations

from md_doctor.fixers import FixResult, apply_fixes


def test_fix_f1_trailing_newline():
    """F1: 파일 끝 newline 1개 보장."""
    result = apply_fixes("text without newline")
    assert result.fixed == "text without newline\n"
    assert "F1" in result.changes


def test_fix_f2_trailing_whitespace():
    """F2: 라인 끝 공백 제거."""
    result = apply_fixes("line 1   \nline 2\t\n")
    assert result.fixed == "line 1\nline 2\n"
    assert "F2" in result.changes


def test_fix_f3_heading_blank_line():
    """F3: H1/H2 헤딩 다음 빈 줄 보장."""
    result = apply_fixes("# Title\n본문")
    assert result.fixed == "# Title\n\n본문"
    assert "F3" in result.changes


def test_fix_f4_empty_heading():
    """F4: 빈 헤딩 제거."""
    result = apply_fixes("# Title\n## \n본문")
    assert "## " not in result.fixed
    assert "F4" in result.changes


def test_fix_f5_strip_bom():
    """F5: UTF-8 BOM 제거."""
    result = apply_fixes("\ufeff# Title")
    assert result.fixed == "# Title"
    assert "F5" in result.changes


def test_fix_f6_crlf_to_lf():
    """F6: CRLF → LF."""
    result = apply_fixes("line 1\r\nline 2\r\n")
    assert result.fixed == "line 1\nline 2\n"
    assert "F6" in result.changes


def test_fix_clean_no_changes():
    """깨끗한 파일 → 변경 0건."""
    text = "# Title\n\n본문\n"
    result = apply_fixes(text)
    assert result.changes == []
    assert result.fixed == text


def test_fix_empty_input():
    """빈 입력 → 변경 0건, 변경 없음."""
    result = apply_fixes("")
    assert result.fixed == ""
    assert result.changes == []


def test_fix_no_heading_no_f3():
    """헤딩 없으면 F3 스킵."""
    result = apply_fixes("본문만\n")
    assert "F3" not in result.changes


def test_fix_combined():
    """복합 변환 (BOM + trailing ws + CRLF)."""
    text = "\ufeff# Title  \r\n본문"
    result = apply_fixes(text)
    assert "F2" in result.changes
    assert "F5" in result.changes
    assert "F6" in result.changes
