# Changelog

All notable changes to **md-doctor** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
