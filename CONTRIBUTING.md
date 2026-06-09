# 기여 가이드 (CONTRIBUTING)

md-doctor에 기여해주셔서 감사합니다! 🎉

## 🧰 개발 환경 세팅

```bash
git clone https://github.com/sigco3111/md-doctor.git
cd md-doctor
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## 🧪 테스트

```bash
# 전체 테스트
pytest

# 커버리지
pytest --cov=md_doctor --cov-report=term-missing

# 특정 테스트만
pytest -k "test_cli_text_output" -v
```

## 🩺 새 검사 모듈 추가하기

### 1단계: `BaseCheck` 서브클래스

```python
# src/md_doctor/checks/my_check.py
from typing import Any, Iterator
from md_doctor.checks import BaseCheck
from md_doctor.models import Diagnosis, Severity


class MyCheck(BaseCheck):
    name = "my-check"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        text: str = context["text"]
        if "TODO" in text:
            yield Diagnosis(
                check=self.name,
                severity=Severity.WARNING,
                message="본문에 TODO가 있습니다.",
                line=None,
                rule="MY001",
            )
```

### 2단계: 레지스트리에 등록

`src/md_doctor/checks/__init__.py` 의 `default_checks()` 에 추가:

```python
def default_checks() -> CheckRegistry:
    from md_doctor.checks.my_check import MyCheck
    # ...
    return CheckRegistry(
        checks=[
            TokenStatsCheck(),
            HeadingConsistencyCheck(),
            MyCheck(),  # ← 추가
        ]
    )
```

### 3단계: 테스트 작성

```python
# tests/test_my_check.py
from md_doctor.checks.my_check import MyCheck


def test_my_check_detects_todo():
    check = MyCheck()
    diagnoses = list(check.run({"text": "TODO: fix this", "lines": [...], "path": ...}))
    assert len(diagnoses) == 1
    assert diagnoses[0].rule == "MY001"
```

### 4단계: PR 제출

```bash
git checkout -b feat/my-check
git add .
git commit -m "feat(checks): add my-check for TODO detection"
git push origin feat/my-check
# GitHub에서 PR 생성
```

## 📐 코딩 컨벤션

- **타입 힌트** — 모든 public 함수에 작성 (mypy 통과)
- **docstring** — NumPy/Google 스타일
- **import 순서** — ruff 가 자동 정렬 (`ruff check --fix`)
- **줄 길이** — 100자 (ruff 기본)
- **한국어 식별자** — 권장하지 않음 (영문 + 한국어 docstring)

## 🐛 버그 리포트

GitHub Issues에 다음 정보를 포함해주세요:
- md-doctor 버전 (`md-doctor --version`)
- Python 버전 (`python --version`)
- 재현 가능한 마크다운 샘플 (최소한)
- 실제 출력 vs 기대 출력
- `md-doctor --format json` 의 결과 (가능하면)

## 💡 기능 제안

GitHub Discussions 또는 Issues의 `enhancement` 라벨로 올려주세요.
특히 다음 분야 환영:
- 🧪 새 검사 모듈 (규칙 ID 명명: `XX001` 형식)
- 🌍 다국어 지원 (영문/일본어 README, 에러 메시지)
- ⚡ 성능 개선 (병렬 처리, 캐시)

## 📜 라이선스

기여하신 코드는 MIT License로 배포됩니다. PR 제출 시 동의한 것으로 간주합니다.
