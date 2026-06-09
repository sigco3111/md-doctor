# Changelog

All notable changes to **md-doctor** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-09

### Added
- 🎯 **안정 API** — 1.0.0 이후 시맨틱 버전 유지, BACKWARD COMPATIBLE 보장
- 📚 `docs/superpowers/api.md` — Public API Reference
- 🧪 5개 정확도 벤치마크 픽스처 — `tests/fixtures/benchmark/`
- 📊 정확도 측정 (`tests/test_benchmark.py`) — recall/precision/F1
- ✅ 6 신규 테스트 (벤치마크), 총 125개

### Notes
- API 변경 0건 (마커만 추가). 모든 v0.5.0 → v1.0.0 사용자 코드 그대로 동작.
- 정확도 벤치마크 임계값: recall ≥ 0.9, precision ≥ 0.8, F1 ≥ 0.85.
- PyPI 정식 배포는 1.0.0+ 후속 (zero-deps 패키지 골격은 준비됨).
- zero-deps 정책 유지.

## [0.5.0] - 2026-06-09

### Added
- 🇰🇷 `--korean` opt-in 플래그 — 한국어 띄어쓰기/맞춤법 검사 (KS1~KS5)
  - KS1: 영어 단어 + 한글 사이 띄어쓰기 권장
  - KS2: 한자 + 한글 사이 띄어쓰기 권장
  - KS3: 숫자 + 한글 단위 사이 띄어쓰기 없음 (WARNING)
  - KS4: 중복 공백 발견
  - KS5: `...` → `…` 권장
- 🛡️ zero-deps 유지 (정규식 기반, 외부 사전 미사용)
- ✅ 12 신규 테스트 (korean_grammar 10 + CLI 2), 총 119개

### Notes
- 기본 비활성 — `--korean` 명시 시에만 활성.
- 다른 검사와 자동 결합 (--korean README.md 만으로 가능).
- zero-deps 정책 유지.

## [0.4.0] - 2026-06-09

### Added
- 🔧 `md-doctor --fix` 플래그 — 6개 안전한 자동 변환
  - F1: 트레일링 newline 추가
  - F2: 트레일링 공백 제거
  - F3: H1/H2 헤딩 다음 빈 줄 보장
  - F4: 빈 헤딩 제거
  - F5: UTF-8 BOM 제거
  - F6: CRLF → LF
- 🧪 `fixers/` 패키지 — `apply_fixes()`, `FixResult`
- 🛡️ 기본 in-place + `--backup .bak`, `--no-backup`/`--dry-run`/`--format json` 옵션
- ✅ 15 신규 테스트 (fixers 10 + fix CLI 5), 총 107개

### Notes
- 진단과 독립 — 사용자가 명시적으로 `--fix` 호출.
- 트리 fix 는 v0.4.0 범위 외 (v0.4.1+).
- zero-deps 정책 유지.

## [0.3.0] - 2026-06-09

### Added
- 🆕 `gfm-lint` check (HC005~HC008) — 리스트 점 일관성, 코드언어 지정, raw HTML, 테이블 정렬
- 🧪 `extractors/code_fence.py` — 코드펜스 + 인라인 코드 마킹 공통 헬퍼
- 🧪 `extractors/html.py` — HTML 태그 추출 (<img>, <a>, <div> 등)
- 🔗 `BrokenImagesCheck` HTML 확장 (BI002) — `<img src>` 추출
- 🔗 `DeadLinksCheck` HTML 확장 (DL002) — `<a href>` 추출
- ✅ 28 신규 테스트 (code_fence 6, html 8, gfm-lint 11, broken/dead +2×2, cli +2), 총 90개

### Changed
- 기본 레지스트리: 4 → 5 활성 검사 (+gfm-lint)
- `extractors/images.py`/`links.py` 가 `code_fence.strip_inline_code` 위임 (동작 100% 보존)

### Notes
- GFM/CommonMark 핵심 규칙 4개 (HC005-008) 만 포함. 작업 목록, 각주 등은 v0.3.x 후속.
- HTML 추출은 정규식 기반. 정밀 파서는 v0.4.0+ 후보.
- zero-deps 정책 유지.

## [0.2.1] - 2026-06-09

### Added
- 🔗 `dead-links` check (DL001) — 로컬 파일 + 외부 URL HEAD 검사
- 🧪 `extractors/links.py` — `LinkRef` + `extract_link_refs()` (인라인/참조/단축/자동 + 정의 테이블)
- 🛡️ 외부 검사는 `urllib` HEAD (zero-deps 유지) + 5초 타임아웃
- ✅ 20 신규 테스트 (추출기 10 + 체크 8 + CLI 2), 총 61개

### Changed
- 기본 레지스트리: 3 → 4 활성 검사 (token-stats, heading-consistency, broken-images, dead-links)
- 종료 코드: 데드 링크 발견 시 1

### Notes
- 외부 URL HEAD 만 검사, GET fallback 없음 (v0.3.0+ 후보).
- 캐시/병렬/재시도 없음 (단순함 우선). v0.3.0+ 에서 추가.
- HTML `<a href>` 추출은 v0.3.0+ 에서 다룸 (YAGNI).

## [0.2.0] - 2026-06-09

### Added
- 🖼️ `broken-images` check (BI001) — 로컬 `![](...)` 참조의 `Path.exists()` 검사
- 🧪 `extractors/images.py` — `ImageRef` + `extract_image_refs()` (재사용 가능한 추출기)
- ✅ 25 신규 테스트 (추출기 11 + 체크 11 + CLI 3), 총 41개

### Changed
- 기본 레지스트리: 2 → 3 활성 검사 (token-stats, heading-consistency, broken-images)
- 종료 코드: 깨진 이미지 발견 시 1 (default `--fail-on warning`)

### Notes
- v0.2.0의 `broken-images` 는 **로컬 파일만** 검사 (zero-deps / offline-first 유지).
- 원격 URL (http/https) 은 `dead-links` 의 범위 (v0.2.1+ 또는 v0.3.0+).
- HTML `<img src>` 추출은 v0.3.0+ 에서 다룸 (YAGNI).

## [0.1.0] - 2026-06-09

### Added
- 🩺 Initial project skeleton
- 📊 `token-stats` check (TS001) — chars/words/lines/headings/lists/tables/code 통계
- 📋 `heading-consistency` check (HC001~HC004) — H1 중복 / 파일명-제목 / 단계 점프 / 빈 헤딩
- 🚧 Stub checks for `dead-links` and `broken-images` (0.2.0+ 예정)
- 🖥️ CLI with `--format {text,json,github}` and `--min-severity` / `--fail-on` flags
- 🐍 Python API: `diagnose_file()`, `diagnose_tree()`, `DoctorReport`, `FileReport`, `Diagnosis`
- 🚨 Exception hierarchy: `MdDoctorError`, `ParseError`, `UnreadableFileError`, `CheckConfigError`
- 🧪 16 smoke tests (pytest)
- ⚙️ GitHub Actions CI workflow
- 📚 Korean README + English appendix
- 📄 MIT License
- 🔌 Zero runtime dependencies (stdlib only)

### Notes
- 0.1.0은 부트스트랩 단계. 활성 검사는 2개 (token-stats, heading-consistency).
- 공개 API: `diagnose_file`, `diagnose_tree`, `Severity`, `Diagnosis`, `DoctorReport`, `FileReport`.
- 1.0.0부터 시맨틱 버저닝 + API 안정성 보장.
