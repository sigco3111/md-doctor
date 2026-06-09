"""도메인 모델 — 모든 모듈이 의존하는 핵심 타입. 순환 import 방지를 위해 분리.

``core`` / ``checks`` / ``cli`` 모두 이 모듈에서 ``Diagnosis``, ``Severity``,
``FileReport``, ``DoctorReport`` 를 가져온다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(str, Enum):
    """진단 심각도."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    @property
    def rank(self) -> int:
        return {"info": 0, "warning": 1, "error": 2}[self.value]


@dataclass(frozen=True)
class Diagnosis:
    """단일 진단 결과 (한 파일에 대해 한 체크가 만든 한 줄)."""

    check: str
    severity: Severity
    message: str
    line: int | None = None
    rule: str | None = None


@dataclass
class FileReport:
    """한 파일에 대한 진단 결과 묶음."""

    path: Path
    diagnoses: list[Diagnosis] = field(default_factory=list)
    byte_size: int = 0
    line_count: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for d in self.diagnoses if d.severity is Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for d in self.diagnoses if d.severity is Severity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for d in self.diagnoses if d.severity is Severity.INFO)

    def has_issues(self, min_severity: Severity = Severity.WARNING) -> bool:
        threshold = min_severity.rank
        return any(d.severity.rank >= threshold for d in self.diagnoses)


@dataclass
class DoctorReport:
    """전체 진단 결과 묶음."""

    files: list[FileReport] = field(default_factory=list)
    scanned_paths: list[Path] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_errors(self) -> int:
        return sum(f.error_count for f in self.files)

    @property
    def total_warnings(self) -> int:
        return sum(f.warning_count for f in self.files)

    @property
    def total_infos(self) -> int:
        return sum(f.info_count for f in self.files)

    def files_with_issues(self, min_severity: Severity = Severity.WARNING) -> list[FileReport]:
        return [f for f in self.files if f.has_issues(min_severity)]


__all__ = [
    "Severity",
    "Diagnosis",
    "FileReport",
    "DoctorReport",
]
