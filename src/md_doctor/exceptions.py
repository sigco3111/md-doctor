"""예외 계층 — 모든 md-doctor 오류는 MdDoctorError의 서브클래스."""

from __future__ import annotations


class MdDoctorError(Exception):
    """md-doctor의 모든 예외의 베이스."""


class ParseError(MdDoctorError):
    """마크다운 파싱 실패 (구문 오류 등)."""


class UnreadableFileError(MdDoctorError):
    """파일 읽기 실패 (존재하지 않음, 권한 없음 등)."""


class CheckConfigError(MdDoctorError):
    """검사 모듈 설정 오류."""
