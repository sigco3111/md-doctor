"""md-doctor — 마크다운 품질 진단 + 후처리 CLI.

한글 메인, 영문 부록.
"""

from md_doctor.core import (
    diagnose_file,
    diagnose_tree,
)
from md_doctor.models import (
    Diagnosis,
    DoctorReport,
    FileReport,
    Severity,
)

__version__ = "0.1.0"

__all__ = [
    # core
    "Diagnosis",
    "DoctorReport",
    "FileReport",
    "Severity",
    "diagnose_file",
    "diagnose_tree",
    # meta
    "__version__",
]
