"""스모크 테스트 — 핵심 API/CLI가 동작하는지만 확인."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from md_doctor import __version__
from md_doctor.checks import default_checks
from md_doctor.cli import main
from md_doctor.core import (
    diagnose_file,
    diagnose_tree,
)
from md_doctor.exceptions import UnreadableFileError
from md_doctor.models import (
    Diagnosis,
    DoctorReport,
    FileReport,
    Severity,
)


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    """정상 마크다운 1개."""
    p = tmp_path / "sample.md"
    p.write_text(
        "# Sample Title\n"
        "\n"
        "본문입니다. 한 줄짜리 짧은 글.\n"
        "\n"
        "## Section A\n"
        "\n"
        "- 항목 1\n"
        "- 항목 2\n"
        "\n"
        "## 1. 단계 1\n"
        "## 2. 단계 2\n"
        "## 3. 단계 3\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def bad_md(tmp_path: Path) -> Path:
    """문제 있는 마크다운 — H1 두 개, 빈 헤딩, 단계 점프."""
    p = tmp_path / "bad.md"
    p.write_text(
        "# First Title\n"
        "\n"
        "본문.\n"
        "\n"
        "# Second Title (이게 H1 두 번째)\n"
        "\n"
        "## \n"
        "\n"
        "## 1. 단계 1\n"
        "## 5. 단계 5 (점프)\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def md_tree(tmp_path: Path) -> Path:
    """재귀 스캔용 트리."""
    (tmp_path / "a.md").write_text("# a\n본문\n", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.md").write_text("# b\n본문\n", encoding="utf-8")
    (sub / "c.txt").write_text("마크다운 아님", encoding="utf-8")  # 무시되어야 함
    return tmp_path


# ---------------------------------------------------------------------------
# 도메인 모델
# ---------------------------------------------------------------------------


def test_version_is_string():
    assert isinstance(__version__, str)
    assert __version__ == "0.2.1"


def test_severity_rank():
    assert Severity.INFO.rank < Severity.WARNING.rank < Severity.ERROR.rank


def test_diagnosis_is_frozen():
    d = Diagnosis(check="x", severity=Severity.INFO, message="m", line=1, rule="R001")
    with pytest.raises(Exception):
        d.message = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 코어
# ---------------------------------------------------------------------------


def test_diagnose_file_emits_info_for_token_stats(sample_md: Path):
    fr = diagnose_file(sample_md)
    stats = [d for d in fr.diagnoses if d.check == "token-stats"]
    assert len(stats) == 1
    assert stats[0].severity is Severity.INFO
    assert "lines=" in stats[0].message


def test_diagnose_file_detects_multiple_h1s(bad_md: Path):
    fr = diagnose_file(bad_md)
    h1_warnings = [d for d in fr.diagnoses if d.rule == "HC001"]
    assert len(h1_warnings) == 1
    assert h1_warnings[0].severity is Severity.WARNING


def test_diagnose_file_detects_step_jump(bad_md: Path):
    fr = diagnose_file(bad_md)
    jumps = [d for d in fr.diagnoses if d.rule == "HC003"]
    assert len(jumps) == 1
    assert "1 → 5" in jumps[0].message


def test_diagnose_tree_skips_non_md(md_tree: Path):
    report = diagnose_tree(md_tree, glob="**/*.md")
    names = {f.path.name for f in report.files}
    assert names == {"a.md", "b.md"}
    assert report.total_files == 2


def test_unreadable_file_raises(tmp_path: Path):
    with pytest.raises(UnreadableFileError):
        diagnose_file(tmp_path / "nonexistent.md")


def test_default_checks_have_unique_names():
    reg = default_checks()
    names = reg.names()
    assert len(names) == len(set(names)), f"중복 검사 이름: {names}"
    # 0.1.0: 2개 활성. 0.2.0: 3개 활성. 0.2.1: 4개 활성. 0.3.0: 5개 활성 (gfm-lint 추가).
    assert "token-stats" in names
    assert "heading-consistency" in names
    assert "broken-images" in names
    assert "dead-links" in names
    assert "gfm-lint" in names


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_text_output(sample_md: Path, capsys):
    rc = main([str(sample_md), "--format", "text", "--min-severity", "info"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "md-doctor v0.2.1" in out
    assert "1개 파일 스캔" in out


def test_cli_json_output(sample_md: Path, capsys):
    rc = main([str(sample_md), "--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["version"] == "0.2.1"
    assert payload["summary"]["total_files"] == 1


def test_cli_github_output(bad_md: Path, capsys):
    rc = main([str(bad_md), "--format", "github", "--min-severity", "warning"])
    assert rc == 1  # 경고 1개 이상 → fail-on warning 기본
    out = capsys.readouterr().out
    assert "::warning file=" in out


def test_cli_list_checks(capsys):
    rc = main(["--list-checks"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "token-stats" in out
    assert "heading-consistency" in out


def test_cli_checks_filter(sample_md: Path, capsys):
    rc = main([str(sample_md), "--checks", "token-stats", "--format", "json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    checks_seen = {d["check"] for f in payload["files"] for d in f["diagnoses"]}
    assert checks_seen == {"token-stats"}


def test_cli_fail_on_never(sample_md: Path, capsys):
    # 이슈 있어도 never면 0
    rc = main([str(sample_md), "--fail-on", "never"])
    assert rc == 0


def test_cli_missing_path(capsys):
    rc = main(["/no/such/path.md"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "존재하지 않습니다" in err


# ---------------------------------------------------------------------------
# broken-images CLI 통합
# ---------------------------------------------------------------------------


def test_cli_runs_broken_images_check(tmp_path: Path, capsys):
    """`--checks broken-images` 로 단독 실행 가능."""
    img = tmp_path / "ok.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    md = tmp_path / "doc.md"
    md.write_text(f"![OK]({img.name})\n", encoding="utf-8")
    rc = main([str(md), "--checks", "broken-images", "--format", "text"])
    assert rc == 0


def test_cli_fails_on_broken_image(tmp_path: Path, capsys):
    """깨진 이미지 → exit 1 + ERROR 라인 출력."""
    md = tmp_path / "doc.md"
    md.write_text("![](missing.png)\n", encoding="utf-8")
    rc = main([str(md), "--format", "text"])
    assert rc == 1  # default --fail-on warning → ERROR 포함 시 1
    out = capsys.readouterr().out
    assert "[BI001]" in out
    assert "missing.png" in out


def test_cli_github_output_includes_broken_image(tmp_path: Path, capsys):
    """GitHub Actions 워크플로 명령에 ERROR 라인 포함."""
    md = tmp_path / "doc.md"
    md.write_text("![](missing.png)\n", encoding="utf-8")
    rc = main([str(md), "--format", "github", "--min-severity", "error"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "::error file=" in out
    assert "missing.png" in out


# ---------------------------------------------------------------------------
# dead-links CLI 통합
# ---------------------------------------------------------------------------


def test_cli_runs_dead_links_check(tmp_path: Path, monkeypatch, capsys):
    """`--checks dead-links` 로 단독 실행 가능 (외부 URL 200 mock)."""
    md = tmp_path / "doc.md"
    md.write_text("[OK](https://example.com)\n", encoding="utf-8")
    monkeypatch.setattr(
        "md_doctor.checks.dead_links.head_request", lambda url, timeout=5.0: 200
    )
    rc = main([str(md), "--checks", "dead-links", "--format", "text"])
    assert rc == 0


def test_cli_fails_on_dead_link(tmp_path: Path, monkeypatch, capsys):
    """데드 링크 → exit 1 + ERROR 라인 출력."""
    md = tmp_path / "doc.md"
    md.write_text("[Dead](https://missing.example.com)\n", encoding="utf-8")
    monkeypatch.setattr(
        "md_doctor.checks.dead_links.head_request", lambda url, timeout=5.0: 404
    )
    rc = main([str(md), "--format", "text"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "[DL001]" in out
    assert "404" in out


# gfm-lint CLI 통합 ----------------------------------------------------


def test_cli_runs_gfm_lint_check(tmp_path: Path, capsys):
    """`--checks gfm-lint` 로 단독 실행 가능."""
    md = tmp_path / "clean.md"
    md.write_text("# Title\n\n- a\n- b\n", encoding="utf-8")
    rc = main([str(md), "--checks", "gfm-lint", "--format", "text"])
    assert rc == 0


def test_cli_fails_on_gfm_lint_warning(tmp_path: Path, capsys):
    """gfm-lint WARNING 발견 시 exit 1."""
    md = tmp_path / "bad.md"
    md.write_text("- a\n* b\n", encoding="utf-8")
    rc = main([str(md), "--format", "text"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "[HC005]" in out
