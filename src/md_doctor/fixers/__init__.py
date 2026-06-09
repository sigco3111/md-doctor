"""자동 후처리 모음 — 6개 안전한 변형.

진단과 독립적으로 동작. 사용자가 명시적으로 ``md-doctor fix`` 호출.
"""

from md_doctor.fixers.transforms import (
    ALL_TRANSFORMS,
    FixResult,
    apply_fixes,
    f1_trailing_newline,
    f2_trailing_whitespace,
    f3_heading_blank_line,
    f4_empty_heading,
    f5_strip_bom,
    f6_crlf_to_lf,
)

__all__ = [
    "ALL_TRANSFORMS",
    "FixResult",
    "apply_fixes",
    "f1_trailing_newline",
    "f2_trailing_whitespace",
    "f3_heading_blank_line",
    "f4_empty_heading",
    "f5_strip_bom",
    "f6_crlf_to_lf",
]
