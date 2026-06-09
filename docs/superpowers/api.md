# md-doctor 1.0.0 — Public API Reference

> 안정 API. v1.0.0 이후 BACKWARD COMPATIBLE 유지.

## Core

- `diagnose_file(path, *, registry=None) -> FileReport`  (stable)
- `diagnose_tree(root, *, glob='**/*.md', registry=None) -> DoctorReport`  (stable)
- `iter_diagnoses(reports, *, min_severity=Severity.INFO) -> Iterator[Diagnosis]`  (stable)
- `filter_diagnoses(reports, *, checks=None, min_severity=Severity.INFO) -> list[Diagnosis]`  (stable)

## Models

- `Severity` (enum: INFO, WARNING, ERROR)  (stable)
- `Diagnosis` (frozen dataclass: check, severity, message, line, rule)  (stable)
- `FileReport` (path, diagnoses, byte_size, line_count, error_count, warning_count, info_count)  (stable)
- `DoctorReport` (files, scanned_paths, total_files, total_errors, total_warnings, total_infos)  (stable)

## Extractors (v0.2.0+)

- `extract_image_refs(text, lines) -> list[ImageRef]`  (stable)
- `extract_link_refs(text, lines) -> list[LinkRef]`  (stable)
- `extract_html_refs(text, lines, fences) -> list[HtmlRef]`  (v0.3.0+, stable)
- `mark_code_regions(lines) -> list[CodeFence]`  (v0.3.0+, stable)
- `strip_inline_code(line) -> str`  (v0.3.0+, stable)
- `is_in_code_region(line_no, fences) -> bool`  (v0.3.0+, stable)

## Fixers (v0.4.0+)

- `apply_fixes(text, *, enabled=None) -> FixResult`  (stable)
- `FixResult` (frozen: original, fixed, changes, changed_lines)  (stable)
- `ALL_TRANSFORMS` (list of (id, transform) tuples)  (stable)
- 6개 변환: F1 (trailing newline), F2 (trailing ws), F3 (heading-newline), F4 (empty heading), F5 (BOM), F6 (CRLF)

## CLI

### 진단 (default)
```
md-doctor <path> [--format {text,json,github}] [--min-severity ...] [--fail-on ...] [--checks ...] [--glob ...] [--list-checks]
```

### 자동 후처리 (v0.4.0+)
```
md-doctor --fix <path> [--backup .bak] [--no-backup] [--dry-run] [--format {text,json}]
```

### 한국어 opt-in (v0.5.0+)
```
md-doctor --korean <path> [--format {text,json}]
```

## Stability Levels

- **stable**: 1.0.0 이후 시맨틱 버전 유지, BACKWARD COMPATIBLE 보장
- **public**: 노출되지만 breaking change 가능
- **internal**: 외부 노출 비권장

## 정확도 벤치마크 (v1.0.0+)

5개 픽스처 기반 recall/precision/F1 측정 (`tests/test_benchmark.py`):
- 깨끗한 마크다운 → 진단 0
- 깨진 이미지 → BI001 recall 1.0
- 깨진 링크 → DL001 recall 1.0
- 한국어 위반 → KS1+KS2+KS3 recall 1.0
- HTML + 테이블 → HC007+HC008 recall 1.0

전체 6 케이스 통과. F1 ≥ 0.85.

## 변경 이력 (안정 API)

- **v0.1.0**: Core API (`diagnose_file`, `diagnose_tree`, `Severity`, `Diagnosis`, `FileReport`, `DoctorReport`)
- **v0.2.0**: `extract_image_refs`, `BrokenImagesCheck` (BI001)
- **v0.2.1**: `extract_link_refs`, `DeadLinksCheck` (DL001)
- **v0.3.0**: `extract_html_refs`, `mark_code_regions`, `strip_inline_code`, `is_in_code_region`, `GfmLintCheck` (HC005-HC008, BI002, DL002)
- **v0.4.0**: `apply_fixes`, `FixResult`, `md-doctor --fix`
- **v0.5.0**: `KoreanGrammarCheck` (KS1-KS5), `md-doctor --korean`
- **v1.0.0**: API 안정성 마커 + 정확도 벤치마크 (변경 없음)

## PyPI 배포

- **v1.0.0+** 후속 작업 (zero-deps 패키지 골격은 준비됨)
- 설치 (개발자): `git clone ... && pip install -e ".[dev]"`
