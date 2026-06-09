"""데드 링크 검사 — 로컬 파일 + 외부 URL HEAD.

원격 URL 은 urllib HEAD 로 검사. 4xx/5xx/타임아웃 → ERROR.
HTML ``<a href>`` 와 인증/쿠키는 0.3.0+ 에서 다룸 (YAGNI).
"""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from md_doctor.checks import BaseCheck
from md_doctor.extractors.links import extract_link_refs
from md_doctor.models import Diagnosis, Severity

_DEFAULT_TIMEOUT = 5.0
_USER_AGENT = "md-doctor/0.2.1 (+https://github.com/sigco3111/md-doctor)"


def head_request(url: str, timeout: float = _DEFAULT_TIMEOUT) -> int:
    """urllib HEAD 요청 → HTTP status code 반환.

    - 405 (Method Not Allowed) 등 HEAD 미지원도 status 로 그대로 반환
    - User-Agent 명시 (default UA 차단 회피)
    - redirect 자동 처리 (urllib 기본)

    Raises
    ------
    urllib.error.URLError
        DNS 실패, timeout, 연결 거부 등.
    TimeoutError, OSError
        시스템 레벨 타임아웃.
    """
    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": _USER_AGENT}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


class DeadLinksCheck(BaseCheck):
    """로컬 + 외부 링크의 유효성 검사 (DL001)."""

    name = "dead-links"

    def run(self, context: dict[str, Any]) -> Iterator[Diagnosis]:
        path: Path = context["path"]
        base_dir = path.parent
        refs = extract_link_refs(context["text"], context["lines"])

        for ref in refs:
            if ref.kind == "definition":
                continue

            if _is_local_path(ref.target):
                yield from _check_local(base_dir, ref)
            else:
                yield from _check_remote(ref)


def _is_local_path(url: str) -> bool:
    """http(s):// 또는 다른 스킴이 없으면 로컬로 간주."""
    return "://" not in url


def _check_local(base_dir: Path, ref) -> Iterator[Diagnosis]:
    try:
        target = _resolve_local(base_dir, ref.target)
    except (ValueError, OSError) as e:
        yield Diagnosis(
            check="dead-links",
            severity=Severity.ERROR,
            message=f"깨진 링크: 경로 해석 실패 '{ref.target}': {e}",
            line=ref.line,
            rule="DL001",
        )
        return

    if not target.exists():
        yield Diagnosis(
            check="dead-links",
            severity=Severity.ERROR,
            message=f"깨진 링크: '{ref.target}' (해상: {target})",
            line=ref.line,
            rule="DL001",
        )
        return

    if target.is_dir():
        yield Diagnosis(
            check="dead-links",
            severity=Severity.ERROR,
            message=f"깨진 링크: '{ref.target}' 은(는) 디렉터리입니다",
            line=ref.line,
            rule="DL001",
        )


def _check_remote(ref) -> Iterator[Diagnosis]:
    try:
        status = head_request(ref.target, timeout=_DEFAULT_TIMEOUT)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        reason = getattr(e, "reason", str(e))
        yield Diagnosis(
            check="dead-links",
            severity=Severity.ERROR,
            message=f"데드 링크: '{ref.target}' (연결 실패: {reason})",
            line=ref.line,
            rule="DL001",
        )
        return

    if status >= 400:
        yield Diagnosis(
            check="dead-links",
            severity=Severity.ERROR,
            message=f"데드 링크: '{ref.target}' (HTTP {status})",
            line=ref.line,
            rule="DL001",
        )


def _resolve_local(base_dir: Path, target: str) -> Path:
    """로컬 경로 해석. fragment(#x) 분리 후 Path 처리.

    fragment-only (``#x``) 는 호출자에서 스킵되므로 여기 도달하지 않음.
    """
    target_no_frag = target.split("#", 1)[0]
    if not target_no_frag:
        raise ValueError("empty path after fragment")
    p = Path(target_no_frag)
    if p.is_absolute():
        return p
    return (base_dir / p).resolve()
