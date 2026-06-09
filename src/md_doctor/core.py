"""코어 진단 로직 — 파일 I/O + 체크 디스패처.

``models`` 만 직접 의존. ``checks`` 는 함수 호출 시점에만 lazy import.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Iterator, Sequence

from md_doctor.exceptions import UnreadableFileError
from md_doctor.models import (
    Diagnosis,
    DoctorReport,
    FileReport,
    Severity,
)

if TYPE_CHECKING:
    from md_doctor.checks import CheckRegistry


__all__ = [
    "Diagnosis",
    "DoctorReport",
    "FileReport",
    "Severity",
    "diagnose_file",
    "diagnose_tree",
    "iter_diagnoses",
    "filter_diagnoses",
]


# 라인 단위 분리용 정규식 (개행 보존)
_LINE_SPLIT = re.compile(r"\n", flags=re.MULTILINE)


def _read_markdown(path: Path) -> str:
    """마크다운 파일을 읽는다. UTF-8 고정, 실패 시 예외."""
    if not path.exists():
        raise UnreadableFileError(f"파일이 존재하지 않습니다: {path}")
    if not path.is_file():
        raise UnreadableFileError(f"파일이 아닙니다 (디렉터리?): {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise UnreadableFileError(
            f"UTF-8 디코딩 실패: {path} — 파일이 UTF-8이 아닙니다 ({e})"
        ) from e
    except PermissionError as e:
        raise UnreadableFileError(f"권한 없음: {path}") from e


def _default_registry() -> "CheckRegistry":
    """기본 검사 레지스트리를 lazy하게 가져온다 (순환 import 회피)."""
    from md_doctor.checks import default_checks

    return default_checks()


def diagnose_file(
    path: Path,
    *,
    registry: "CheckRegistry | None" = None,
) -> FileReport:
    """한 마크다운 파일을 진단한다.

    Parameters
    ----------
    path:
        진단할 .md 파일 경로.
    registry:
        사용할 검사 레지스트리. None이면 기본 검사 세트.
    """
    registry = registry or _default_registry()
    text = _read_markdown(path)
    lines = _LINE_SPLIT.split(text)

    file_report = FileReport(
        path=path,
        byte_size=len(text.encode("utf-8")),
        line_count=len(lines),
    )

    context = {
        "text": text,
        "lines": lines,
        "path": path,
    }

    for diagnosis in registry.run(context):
        file_report.diagnoses.append(diagnosis)
    return file_report


def diagnose_tree(
    root: Path,
    *,
    glob: str = "**/*.md",
    registry: "CheckRegistry | None" = None,
) -> DoctorReport:
    """디렉터리 트리 전체를 진단한다."""
    if not root.exists():
        raise UnreadableFileError(f"경로가 존재하지 않습니다: {root}")
    if not root.is_dir():
        raise UnreadableFileError(f"디렉터리가 아닙니다: {root}")

    registry = registry or _default_registry()
    files = sorted(p for p in root.glob(glob) if p.is_file())

    report = DoctorReport(scanned_paths=[root])
    for f in files:
        report.files.append(diagnose_file(f, registry=registry))
    return report


def iter_diagnoses(
    reports: Iterable[FileReport],
    *,
    min_severity: Severity = Severity.INFO,
) -> Iterator[Diagnosis]:
    """리포트들을 단일 진단 스트림으로 평탄화."""
    threshold = min_severity.rank
    for fr in reports:
        for d in fr.diagnoses:
            if d.severity.rank >= threshold:
                yield d


def filter_diagnoses(
    reports: Sequence[FileReport],
    *,
    checks: Sequence[str] | None = None,
    min_severity: Severity = Severity.INFO,
) -> list[Diagnosis]:
    """리포트들에서 진단을 필터링하여 리스트로 반환."""
    out: list[Diagnosis] = []
    for d in iter_diagnoses(reports, min_severity=min_severity):
        if checks is None or d.check in checks:
            out.append(d)
    return out
