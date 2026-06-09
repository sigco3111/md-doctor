"""KoreanGrammarCheck 단위 테스트 — KS1~KS5 5개 규칙."""

from __future__ import annotations

from pathlib import Path
import tempfile

from md_doctor import Severity
from md_doctor.core import diagnose_file


def _run(text: str) -> list:
    """테스트 헬퍼: text 를 임시 파일로 진단, korean-grammar 결과만 반환."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(text)
        path = Path(f.name)
    try:
        fr = diagnose_file(path)
        return [d for d in fr.diagnoses if d.check == "korean-grammar"]
    finally:
        path.unlink()


def test_ks1_english_korean_no_space():
    """KS1: 영어+한글 띄어쓰기 권장."""
    diags = _run("Python은 좋은 언어다")
    ks1 = [d for d in diags if d.rule == "KS1"]
    assert len(ks1) == 1
    assert ks1[0].severity is Severity.INFO


def test_ks2_hanja_korean_no_space():
    """KS2: 한자+한글 띄어쓰기 권장."""
    diags = _run("中文언어를 배운다")
    ks2 = [d for d in diags if d.rule == "KS2"]
    assert len(ks2) == 1


def test_ks3_number_korean_unit_with_space():
    """KS3: 숫자+단위 사이 띄어쓰기 위반 (WARNING)."""
    diags = _run("10 개 있다")
    ks3 = [d for d in diags if d.rule == "KS3"]
    assert len(ks3) == 1
    assert ks3[0].severity is Severity.WARNING


def test_ks4_double_space():
    """KS4: 중복 공백."""
    diags = _run("a  b")
    ks4 = [d for d in diags if d.rule == "KS4"]
    assert len(ks4) == 1
    assert ks4[0].severity is Severity.INFO


def test_ks5_three_dots():
    """KS5: '...' → '…' 권장."""
    diags = _run("생각...")
    ks5 = [d for d in diags if d.rule == "KS5"]
    assert len(ks5) == 1
    assert ks5[0].severity is Severity.INFO


def test_normal_korean_no_diagnosis():
    """정상 문장 → 0건."""
    diags = _run("한글은 좋습니다. English 도 좋습니다.")
    assert all(d.rule not in ("KS1", "KS2", "KS3", "KS4", "KS5") for d in diags)


def test_code_fence_ignored():
    """코드펜스 내부 무시."""
    diags = _run("```\nPython은\n```")
    assert diags == []


def test_inline_code_ignored():
    """인라인 코드 내부 무시."""
    diags = _run("use `Python은` here")
    assert diags == []


def test_combined():
    """복합 (KS1+KS3+KS5 동시)."""
    diags = _run("Python은 좋다. 10 개 있다. ...")
    rules = {d.rule for d in diags}
    assert "KS1" in rules
    assert "KS3" in rules
    assert "KS5" in rules


def test_empty_no_diagnosis():
    """빈 파일 → 0건."""
    diags = _run("")
    assert diags == []
