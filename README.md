# md-doctor 🩺

> **마크다운 품질 진단 + 후처리 CLI — 데드 링크, 깨진 이미지, 한국어 헤딩 일관성, 토큰 효율 통계**
>
> [English](#english) | **한국어** (이 문서)

[![CI](https://github.com/sigco3111/md-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/sigco3111/md-doctor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](#-설치)

## 🎯 왜 md-doctor 인가?

한국어 개발자/문서 작성자가 마크다운을 다루다 보면 이런 문제가 반복됩니다:

- ❌ GitHub README는 잘 쓰지만 **깨진 이미지 링크**는 알 수가 없다
- ❌ Notion에서 export 한 마크다운에 **H1이 3개씩** 들어와 있다
- ❌ LLM에 넣을 문서 토큰 수가 **너무 커서 비용이 폭증**
- ❌ `pyhwp`로 변환한 산출물에 **dead link**가 섞여 들어왔다
- ❌ `markdownlint` 는 한국어 헤딩 / 파일명 일치 / 단계 점프 같은 건 검사 안 해줌

**md-doctor** 는 이 갭을 채웁니다:

- ✅ **오프라인 우선** — 인터넷 없이도 기본 검사 동작
- ✅ **zero-deps** — Python 표준 라이브러리만 사용 (선택 의존성 없음)
- ✅ **한국어 특화** — 헤딩 일관성, 파일명 매칭, 토큰 통계
- ✅ **CI 친화** — `--format github` 으로 GitHub Actions 워크플로 명령 출력
- ✅ **pre-commit 친화** — stdin 파이프 + 종료 코드 0/1
- ✅ **hwp2md와 페어링** — 변환 결과의 품질을 즉시 검증

## 📦 설치

```bash
# PyPI (곧 출시 예정, 0.2.0+)
pip install md-doctor

# 소스에서 (개발자)
git clone https://github.com/sigco3111/md-doctor.git
cd md-doctor
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

> **의존성: zero.** Python 3.9+ 표준 라이브러리만 사용합니다.

## 🚀 빠른 시작

### CLI

```bash
# 단일 파일 진단 (사람이 읽을 출력)
md-doctor README.md

# 디렉터리 전체 재귀 스캔
md-doctor ./docs/

# JSON 형식 (도구 체이닝)
md-doctor README.md --format json -o report.json

# GitHub Actions 워크플로 명령 (PR 주석에 자동 노출)
md-doctor ./docs/ --format github --min-severity warning

# 특정 검사만 활성화
md-doctor README.md --checks token-stats,heading-consistency

# 사용 가능한 검사 목록
md-doctor --list-checks

# 자동 후처리 (안전한 변환만, in-place + .bak 백업)
md-doctor --fix README.md
md-doctor --fix README.md --dry-run      # 변경 사항만 표시
md-doctor --fix README.md --no-backup    # 백업 생략
md-doctor --fix README.md --format json -o diff.json
```

### Python API

```python
from pathlib import Path
from md_doctor import diagnose_file, diagnose_tree, Severity

# 단일 파일
report = diagnose_file(Path("README.md"))
print(f"오류 {report.error_count} / 경고 {report.warning_count} / 정보 {report.info_count}")

for d in report.diagnoses:
    loc = f":{d.line}" if d.line else ""
    print(f"[{d.severity.value.upper()}]{loc} {d.message}")

# 디렉터리 트리
tree = diagnose_tree(Path("./docs/"))
for fr in tree.files_with_issues(min_severity=Severity.WARNING):
    print(f"⚠️  {fr.path}: {fr.warning_count}개 경고")
```

## 🩺 검사 모듈 (Checks)

| 검사 | 규칙 ID | 심각도 | 0.1.0 | 설명 |
|------|---------|--------|:-----:|------|
| **token-stats** | TS001 | INFO | ✅ | 글자/단어/줄/리스트/표/코드 통계 (LLM 입력 토큰 효율 측정) |
| **heading-consistency** | HC001 | WARNING | ✅ | H1이 2개 이상이면 경고 |
| | HC002 | INFO | ✅ | 파일명 ↔ 첫 H1 일치 검사 |
| | HC003 | INFO | ✅ | 단계 헤딩이 1씩 증가하는지 |
| | HC004 | WARNING | ✅ | 빈 헤딩 |
| **broken-images** | BI001 | ERROR | ✅ 0.2.0 | `![](...)` 참조의 유효성 (로컬) |
| | BI002 | ERROR | ✅ 0.3.0 | `<img src>` HTML 추출 |
| **dead-links** | DL001 | ERROR | ✅ 0.2.1 | 외부/내부 링크 HEAD (5s 타임아웃) |
| | DL002 | ERROR | ✅ 0.3.0 | `<a href>` HTML 추출 |
| **gfm-lint** | HC005-HC008 | WARNING/INFO | ✅ 0.3.0 | GFM/CommonMark 규칙 |

> **0.1.0**: token-stats + heading-consistency 활성.
> **0.2.0**: + broken-images (로컬) 활성.
> **0.2.1**: + dead-links (로컬 + URL HEAD) 활성.
> **0.3.0**: + gfm-lint (HC005-008) + HTML `<img>`/`<a>` 추출.

### 출력 예시

```
🔍 md-doctor v0.1.0 — 1개 파일 스캔
   ❌ 오류 0  ⚠️  경고 2  ℹ️  정보 3

📄 /tmp/sample.md
  ℹ️ :1 [TS001] chars=72 words=18 lines=11 headings=5 lists=0 tables=0 code=0
  ⚠️ :5 [HC001] H1 헤딩이 2개입니다 (권장: 1개).
  ℹ️ :1 [HC002] 파일명 'sample' 과 첫 H1 'Sample Title' 이 다릅니다.
  ℹ️ :10 [HC003] 단계 헤딩 점프: 1 → 5 (1씩 증가 권장).
  ⚠️ :7 [HC004] 빈 헤딩입니다.
```

## ⚙️ GitHub Action

```yaml
# .github/workflows/md-doctor.yml
name: md-doctor
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: sigco3111/md-doctor@v1
        with:
          path: docs/
          min-severity: warning
```

## 🛠️ 사용 사례

- **HWP/HWPX → Markdown 변환 후 검증** — [sigco3111/hwp2md](https://github.com/sigco3111/hwp2md) 산출물의 dead link / broken image 즉시 확인
- **LLM RAG 코퍼스 품질 관리** — 토큰 통계 + 헤딩 일관성으로 인덱싱 전 정제
- **기술 블로그 운영** — Notion/Confluence export 마크다운의 위생 점검
- **학위 논문 마이그레이션** — PDF→MD 변환 결과의 구조 검증
- **다국어 문서 일관성** — 한국어/영문 README의 헤딩 구조 점검
- **pre-commit 훅** — `md-doctor docs/ --fail-on warning` 으로 PR 차단

## 🗺️ 로드맵

- **0.1.0** ✅ — 프로젝트 부트스트랩, CLI 뼈대, token-stats + heading-consistency
- **0.2.0** ✅ — broken-images (로컬) 활성화
- **0.2.1** ✅ — dead-links (로컬 + URL HEAD) 활성화
- **0.3.0** ✅ — GFM/CommonMark 린트 (gfm-lint + HTML 추출)
- **0.4.0** ✅ — md-doctor --fix (6개 안전 변환)
- **0.3.0** — GFM/CommonMark 규칙 린트, 코드펜스 내부 인식 정확도 개선
- **0.4.0** — `md-doctor fix` 자동 후처리 (안전한 변환만: trailing newline 등)
- **0.5.0** — 한국어 띄어쓰기/맞춤법 검사 (외부 사전 연동, opt-in)
- **1.0.0** — 안정 API + 정확도 벤치마크 + PyPI 정식 배포

## 🤝 기여하기

기여 환영합니다! 자세한 절차는 [CONTRIBUTING.md](CONTRIBUTING.md) 참고.

특히 다음 분야:
- 🐛 **엣지 케이스 픽스처** — 한국어 정부/공공 문서, 마크다운 export 샘플
- 🧪 **새 검사 모듈** — `BaseCheck` 서브클래스 1개당 PR 1개 권장
- 🌐 **i18n** — 영문/일본어 README 번역, 다국어 에러 메시지
- ⚡ **성능** — `dead-links` 의 병렬 HEAD 요청 + 디스크 캐시

## 📄 라이선스

[MIT License](LICENSE) — 자유롭게 사용/수정/배포하세요.

## 🙏 감사의 말

- [markdownlint](https://github.com/DavidAnson/markdownlint) — GFM 규칙 참고
- [remark](https://github.com/remarkjs/remark) — AST 파싱 아이디어
- [sigco3111/hwp2md](https://github.com/sigco3111/hwp2md) — 페어링 도구
- 모든 기여자와 이슈 제보자들

---

<a id="english"></a>

## English

**md-doctor** is a zero-dependency CLI that diagnoses Markdown quality:
token statistics, heading consistency (H1 / filename / step jumps), and
(in 0.2.0+) dead link / broken image detection. Korean-aware by design.
Pairs naturally with [sigco3111/hwp2md](https://github.com/sigco3111/hwp2md)
to validate the output of Korean HWP→MD conversion pipelines.

- 🏠 Homepage: <https://github.com/sigco3111/md-doctor>
- 🐛 Issues: <https://github.com/sigco3111/md-doctor/issues>
- 📦 PyPI: coming with 1.0.0

```bash
git clone https://github.com/sigco3111/md-doctor.git
cd md-doctor
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
md-doctor README.md
```

Made with ❤️ in Seoul for the open-source community.
