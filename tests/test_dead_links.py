"""DeadLinksCheck 통합 테스트 — 로컬 + 원격 (mock) 검사."""

from __future__ import annotations

import urllib.error
from pathlib import Path

import pytest

from md_doctor import Severity
from md_doctor.core import diagnose_file, diagnose_tree

# 픽스처 헬퍼 ----------------------------------------------------------


@pytest.fixture
def mock_head_ok(monkeypatch):
    """기본 mock: 모든 URL → 200 OK."""

    def _fake(url, timeout=5.0):
        return 200

    monkeypatch.setattr("md_doctor.checks.dead_links.head_request", _fake)
    return _fake


@pytest.fixture
def mock_head_404(monkeypatch):
    """모든 URL → 404."""

    def _fake(url, timeout=5.0):
        return 404

    monkeypatch.setattr("md_doctor.checks.dead_links.head_request", _fake)
    return _fake


@pytest.fixture
def mock_head_timeout(monkeypatch):
    """모든 URL → URLError (timeout)."""

    def _fake(url, timeout=5.0):
        raise urllib.error.URLError("timed out")

    monkeypatch.setattr("md_doctor.checks.dead_links.head_request", _fake)
    return _fake


# L8. 로컬 정상 ---------------------------------------------------------


def test_local_existing_file_no_diagnosis(tmp_path: Path):
    target = tmp_path / "doc.md"
    target.write_text("hello\n", encoding="utf-8")
    md = tmp_path / "index.md"
    md.write_text(f"[OK]({target.name})\n", encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert dl == []


# L9. 로컬 깨진 → ERROR --------------------------------------------------


def test_local_missing_file_emits_error(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text("[X](missing.md)\n", encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert len(dl) == 1
    assert dl[0].severity is Severity.ERROR
    assert dl[0].rule == "DL001"
    assert dl[0].line == 1
    assert "missing.md" in dl[0].message


# L10. 로컬 ../ 정규화 --------------------------------------------------


def test_local_parent_path_normalized(tmp_path: Path):
    target = tmp_path / "x.md"
    target.write_text("hello\n", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    md = sub / "doc.md"
    md.write_text("[A](../x.md)\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "dead-links" for d in fr.diagnoses)


# L11. 원격 200 → 진단 0 -----------------------------------------------


def test_remote_200_no_diagnosis(tmp_path: Path, mock_head_ok):
    md = tmp_path / "doc.md"
    md.write_text("[OK](https://example.com)\n", encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert dl == []


# L12. 원격 404 → ERROR -------------------------------------------------


def test_remote_404_emits_error(tmp_path: Path, mock_head_404):
    md = tmp_path / "doc.md"
    md.write_text("[Dead](https://example.com/missing)\n", encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert len(dl) == 1
    assert dl[0].severity is Severity.ERROR
    assert dl[0].rule == "DL001"
    assert "404" in dl[0].message


# L13. 원격 타임아웃 → ERROR --------------------------------------------


def test_remote_timeout_emits_error(tmp_path: Path, mock_head_timeout):
    md = tmp_path / "doc.md"
    md.write_text("[Slow](https://slow.example.com)\n", encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert len(dl) == 1
    assert dl[0].severity is Severity.ERROR
    assert "연결 실패" in dl[0].message


# L14. 트리 스캔 --------------------------------------------------------


def test_diagnose_tree_handles_dead_links_in_subdirs(
    tmp_path: Path, mock_head_ok
):
    (tmp_path / "a.md").write_text("[X](missing.md)\n", encoding="utf-8")
    ok = tmp_path / "ok.md"
    ok.write_text("hello\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("[OK](ok.md)\n", encoding="utf-8")
    report = diagnose_tree(tmp_path)
    dl_by_file = {
        f.path.name: [d for d in f.diagnoses if d.check == "dead-links"]
        for f in report.files
    }
    assert len(dl_by_file["a.md"]) == 1
    assert dl_by_file["b.md"] == []


# 보너스: 디렉터리 참조 → ERROR -----------------------------------------


def test_local_directory_emits_error(tmp_path: Path):
    d = tmp_path / "docs"
    d.mkdir()
    md = tmp_path / "index.md"
    md.write_text("[D](docs)\n", encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert len(dl) == 1
    assert "디렉터리" in dl[0].message


# DL002: HTML <a href> --------------------------------------------------


def test_html_anchor_dead_emits_dl002(tmp_path: Path, mock_head_404):
    md = tmp_path / "doc.md"
    md.write_text('<a href="https://missing.example.com">x</a>\n', encoding="utf-8")
    fr = diagnose_file(md)
    dl002 = [d for d in fr.diagnoses if d.rule == "DL002"]
    assert len(dl002) == 1
    assert dl002[0].severity is Severity.ERROR
    assert "404" in dl002[0].message


def test_html_anchor_existing_no_diagnosis(tmp_path: Path, mock_head_ok):
    md = tmp_path / "doc.md"
    md.write_text('<a href="https://example.com">x</a>\n', encoding="utf-8")
    fr = diagnose_file(md)
    dl = [d for d in fr.diagnoses if d.check == "dead-links"]
    assert dl == []
