"""GfmLintCheck 단위 테스트 — HC005~008 4개 규칙."""

from __future__ import annotations

from pathlib import Path

from md_doctor import Severity
from md_doctor.core import diagnose_file


def test_clean_markdown_no_diagnosis(tmp_path: Path):
    md = tmp_path / "clean.md"
    md.write_text(
        "# Title\n\n- item 1\n- item 2\n\n```python\nprint()\n```\n",
        encoding="utf-8",
    )
    fr = diagnose_file(md)
    assert all(d.check != "gfm-lint" for d in fr.diagnoses)


def test_hc005_mixed_bullets_warning(tmp_path: Path):
    md = tmp_path / "mixed.md"
    md.write_text("- a\n* b\n+ c\n", encoding="utf-8")
    fr = diagnose_file(md)
    hc005 = [d for d in fr.diagnoses if d.rule == "HC005"]
    assert len(hc005) == 1
    assert hc005[0].severity is Severity.WARNING


def test_hc005_mixed_ordered_warning(tmp_path: Path):
    md = tmp_path / "ordered.md"
    md.write_text("1. a\n2) b\n", encoding="utf-8")
    fr = diagnose_file(md)
    hc005 = [d for d in fr.diagnoses if d.rule == "HC005"]
    assert any("." in d.message and ")" in d.message for d in hc005)


def test_hc005_consistent_no_warning(tmp_path: Path):
    md = tmp_path / "ok.md"
    md.write_text("- a\n- b\n1. c\n2. d\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.rule != "HC005" for d in fr.diagnoses)


def test_hc006_code_no_language_info(tmp_path: Path):
    md = tmp_path / "code.md"
    md.write_text("```\ncode\n```\n", encoding="utf-8")
    fr = diagnose_file(md)
    hc006 = [d for d in fr.diagnoses if d.rule == "HC006"]
    assert len(hc006) == 1
    assert hc006[0].severity is Severity.INFO


def test_hc006_code_with_language_no_diagnosis(tmp_path: Path):
    md = tmp_path / "code.md"
    md.write_text("```python\nprint()\n```\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.rule != "HC006" for d in fr.diagnoses)


def test_hc007_raw_html_warning(tmp_path: Path):
    md = tmp_path / "raw.md"
    md.write_text("<div>content</div>\n", encoding="utf-8")
    fr = diagnose_file(md)
    hc007 = [d for d in fr.diagnoses if d.rule == "HC007"]
    assert len(hc007) == 1
    assert hc007[0].severity is Severity.WARNING
    assert "div" in hc007[0].message


def test_hc007_gfm_compatible_no_warning(tmp_path: Path):
    md = tmp_path / "gfm.md"
    md.write_text("<br>\n<sub>2</sub>\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.rule != "HC007" for d in fr.diagnoses)


def test_hc008_misaligned_table_warning(tmp_path: Path):
    md = tmp_path / "table.md"
    md.write_text("| a | b | c |\n|---|---|\n| 1 | 2 | 3 |\n", encoding="utf-8")
    fr = diagnose_file(md)
    hc008 = [d for d in fr.diagnoses if d.rule == "HC008"]
    assert len(hc008) == 1
    assert hc008[0].severity is Severity.WARNING


def test_hc008_aligned_table_no_warning(tmp_path: Path):
    md = tmp_path / "table.md"
    md.write_text(
        "| a | b | c |\n|---|---|---|\n| 1 | 2 | 3 |\n",
        encoding="utf-8",
    )
    fr = diagnose_file(md)
    assert all(d.rule != "HC008" for d in fr.diagnoses)


def test_gfm_lint_in_code_fence_ignored(tmp_path: Path):
    md = tmp_path / "code.md"
    md.write_text("```\n- a\n* b\n<div>x</div>\n```\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "gfm-lint" for d in fr.diagnoses)
