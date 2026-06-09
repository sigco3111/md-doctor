"""BrokenImagesCheck 통합 테스트 — 경로 해석 + 진단 생성."""

from __future__ import annotations

from pathlib import Path

from md_doctor import Severity
from md_doctor.core import diagnose_file, diagnose_tree

# 픽스처 헬퍼 ----------------------------------------------------------


def _write_png(p: Path) -> None:
    """가짜 PNG 헤더 (8바이트) — Path.exists() 만 필요."""
    p.write_bytes(b"\x89PNG\r\n\x1a\n")


# S1. Happy path --------------------------------------------------------


def test_existing_image_produces_no_diagnosis(tmp_path: Path):
    """존재하는 이미지 → 진단 0개."""
    img = tmp_path / "a.png"
    _write_png(img)
    md = tmp_path / "doc.md"
    md.write_text(f"![Alt]({img.name})\n", encoding="utf-8")
    fr = diagnose_file(md)
    bi = [d for d in fr.diagnoses if d.check == "broken-images"]
    assert bi == []


# S2. 깨진 이미지 → ERROR ----------------------------------------------


def test_missing_image_emits_error(tmp_path: Path):
    """없는 이미지 → ERROR + BI001 + 정확한 line."""
    md = tmp_path / "doc.md"
    md.write_text("![X](missing.png)\n", encoding="utf-8")
    fr = diagnose_file(md)
    bi = [d for d in fr.diagnoses if d.check == "broken-images"]
    assert len(bi) == 1
    assert bi[0].severity is Severity.ERROR
    assert bi[0].rule == "BI001"
    assert bi[0].line == 1
    assert "missing.png" in bi[0].message


# S3. 코드펜스 내부 이미지 무시 -----------------------------------------


def test_ignores_code_fence_images(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text("```\n![](missing.png)\n```\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "broken-images" for d in fr.diagnoses)


# S4. 인라인 코드 내부 이미지 무시 --------------------------------------


def test_ignores_inline_code_images(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text("`![](missing.png)` 참조는 코드.\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "broken-images" for d in fr.diagnoses)


# S5. 원격 URL 스킵 ----------------------------------------------------


def test_skips_remote_url(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text("![Remote](https://example.com/x.png)\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "broken-images" for d in fr.diagnoses)


# S6. data: URL 스킵 ---------------------------------------------------


def test_skips_data_url(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text("![Inlined](data:image/png;base64,abc)\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "broken-images" for d in fr.diagnoses)


# S7. 서브디렉터리 상대경로 해석 ----------------------------------------


def test_resolves_subdir_relative(tmp_path: Path):
    sub = tmp_path / "assets"
    sub.mkdir()
    img = sub / "ok.png"
    _write_png(img)
    md = sub / "doc.md"
    md.write_text("![A](./ok.png)\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "broken-images" for d in fr.diagnoses)


# S8. ../ 경로 정규화 --------------------------------------------------


def test_resolves_parent_path(tmp_path: Path):
    img = tmp_path / "x.png"
    _write_png(img)
    sub = tmp_path / "sub"
    sub.mkdir()
    md = sub / "doc.md"
    md.write_text("![A](../x.png)\n", encoding="utf-8")
    fr = diagnose_file(md)
    assert all(d.check != "broken-images" for d in fr.diagnoses)


# S9. 디렉터리 참조 → ERROR --------------------------------------------


def test_directory_target_emits_error(tmp_path: Path):
    d = tmp_path / "images"
    d.mkdir()
    md = tmp_path / "doc.md"
    md.write_text("![A](images)\n", encoding="utf-8")
    fr = diagnose_file(md)
    bi = [d for d in fr.diagnoses if d.check == "broken-images"]
    assert len(bi) == 1
    assert "디렉터리" in bi[0].message


# S10. 한 줄에 여러 이미지 --------------------------------------------


def test_multiple_images_per_line(tmp_path: Path):
    md = tmp_path / "doc.md"
    md.write_text("![A](missing1.png) ![B](missing2.png)\n", encoding="utf-8")
    fr = diagnose_file(md)
    bi = [d for d in fr.diagnoses if d.check == "broken-images"]
    assert len(bi) == 2
    assert all(d.line == 1 for d in bi)


# S14. 트리 스캔: .md 옆 images/ 디렉터리 ------------------------------


def test_diagnose_tree_handles_broken_images_in_subdirs(tmp_path: Path):
    (tmp_path / "a.md").write_text("![A](missing.png)\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("![B](ok.png)\n", encoding="utf-8")
    _write_png(tmp_path / "ok.png")
    report = diagnose_tree(tmp_path)
    bi_by_file = {
        f.path.name: [d for d in f.diagnoses if d.check == "broken-images"]
        for f in report.files
    }
    assert len(bi_by_file["a.md"]) == 1
    assert bi_by_file["b.md"] == []
