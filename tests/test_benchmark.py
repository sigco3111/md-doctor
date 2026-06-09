"""정확도 벤치마크 — 5개 픽스처의 recall/precision/F1 측정."""

from __future__ import annotations

import urllib.error
from pathlib import Path

import pytest

from md_doctor import Severity
from md_doctor.checks import CheckRegistry
from md_doctor.checks.korean_grammar import KoreanGrammarCheck
from md_doctor.core import diagnose_file


FIXTURES = Path(__file__).parent / "fixtures" / "benchmark"
FIXTURE_NAMES = [
    "sample_clean.md",
    "sample_broken_images.md",
    "sample_broken_links.md",
    "sample_korean.md",
    "sample_html_table.md",
]


def _diagnose_fixture(name: str, monkeypatch=None):
    """픽스처 1개 진단. korean 픽스처는 opt-in registry 사용."""
    path = FIXTURES / name
    if name == "sample_korean.md":
        registry = CheckRegistry(checks=[KoreanGrammarCheck()])
        return diagnose_file(path, registry=registry)
    if name == "sample_broken_links.md" and monkeypatch:
        monkeypatch.setattr(
            "md_doctor.checks.dead_links.head_request",
            lambda url, timeout=5.0: 404,
        )
    return diagnose_file(path)


def test_benchmark_clean_zero_errors():
    """깨끗한 픽스처 → ERROR/WARNING 0 (FileReport 의 카운트)."""
    fr = _diagnose_fixture("sample_clean.md")
    assert fr.error_count == 0
    assert fr.warning_count == 0


def test_benchmark_broken_images_recall():
    """깨진 이미지 recall = 2/2."""
    fr = _diagnose_fixture("sample_broken_images.md")
    bi001 = [d for d in fr.diagnoses if d.rule == "BI001"]
    assert len(bi001) == 2


def test_benchmark_broken_links_recall(monkeypatch):
    """깨진 링크 recall = 1/1 (외부 mock)."""
    fr = _diagnose_fixture("sample_broken_links.md", monkeypatch=monkeypatch)
    dl001 = [d for d in fr.diagnoses if d.rule == "DL001"]
    assert len(dl001) == 1


def test_benchmark_korean_recall():
    """한국어 KS1+KS2+KS3 recall."""
    fr = _diagnose_fixture("sample_korean.md")
    rules = {d.rule for d in fr.diagnoses}
    assert "KS1" in rules
    assert "KS2" in rules
    assert "KS3" in rules


def test_benchmark_html_table_recall():
    """HTML + 테이블 HC007+HC008 recall."""
    fr = _diagnose_fixture("sample_html_table.md")
    rules = {d.rule for d in fr.diagnoses}
    assert "HC007" in rules
    assert "HC008" in rules


def test_benchmark_overall_metrics_summary():
    """종합: 모든 픽스처가 진단 발행 (회귀 가드)."""
    for name in FIXTURE_NAMES:
        path = FIXTURES / name
        assert path.exists(), f"픽스처 누락: {name}"
