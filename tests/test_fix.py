"""md-doctor --fix CLI 통합 테스트."""

from __future__ import annotations

import json
from pathlib import Path

from md_doctor.cli import main


def test_cli_fix_creates_backup(tmp_path: Path, capsys):
    """기본: 백업 생성 + in-place."""
    md = tmp_path / "test.md"
    md.write_text("no newline", encoding="utf-8")
    rc = main(["--fix", str(md)])
    assert rc == 0
    assert (tmp_path / "test.md.bak").exists()
    assert md.read_text(encoding="utf-8") == "no newline\n"


def test_cli_fix_no_backup(tmp_path: Path):
    """--no-backup: 백업 생략."""
    md = tmp_path / "test.md"
    md.write_text("no newline", encoding="utf-8")
    rc = main(["--fix", str(md), "--no-backup"])
    assert rc == 0
    assert not (tmp_path / "test.md.bak").exists()
    assert md.read_text(encoding="utf-8") == "no newline\n"


def test_cli_fix_dry_run(tmp_path: Path):
    """--dry-run: 원본 보존."""
    md = tmp_path / "test.md"
    original = "no newline"
    md.write_text(original, encoding="utf-8")
    rc = main(["--fix", str(md), "--dry-run"])
    assert rc == 0
    assert md.read_text(encoding="utf-8") == original


def test_cli_fix_json_output(tmp_path: Path, capsys):
    """--format json: payload 출력."""
    md = tmp_path / "test.md"
    md.write_text("no newline", encoding="utf-8")
    rc = main(["--fix", str(md), "--no-backup", "--format", "json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert "F1" in payload["applied"]


def test_cli_diagnose_still_works(tmp_path: Path, capsys):
    """기존 md-doctor <path> (diagnose) 호환성."""
    md = tmp_path / "test.md"
    md.write_text("# Title\n\n- a\n- b\n", encoding="utf-8")
    rc = main([str(md), "--format", "text"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "md-doctor" in out
