# Changelog

All notable changes to **md-doctor** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
