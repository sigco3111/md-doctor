"""CLI 진입점 — ``md-doctor <path>`` 또는 ``python -m md_doctor``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from md_doctor import __version__
from md_doctor.core import (
    Severity,
    diagnose_file,
    diagnose_tree,
)
from md_doctor.exceptions import MdDoctorError


_SEVERITY_BADGE = {
    Severity.INFO: "ℹ️ ",
    Severity.WARNING: "⚠️ ",
    Severity.ERROR: "❌",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md-doctor",
        description="마크다운 품질 진단 + 후처리 CLI",
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=None,
        help="진단할 .md 파일 또는 디렉터리 (--list-checks와 함께 쓰면 생략 가능)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="리포트 출력 파일 (생략 시 stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "github"],
        default="text",
        help="출력 포맷 (기본: text)",
    )
    parser.add_argument(
        "--min-severity",
        choices=["info", "warning", "error"],
        default="info",
        help="표시할 최소 심각도 (기본: info)",
    )
    parser.add_argument(
        "--glob",
        default="**/*.md",
        help="디렉터리 진단 시 매칭 glob (기본: **/*.md)",
    )
    parser.add_argument(
        "--fail-on",
        choices=["info", "warning", "error", "never"],
        default="warning",
        help="비정상 종료할 최소 심각도 (기본: warning)",
    )
    parser.add_argument(
        "--checks",
        default=None,
        help="활성화할 검사 모듈 (콤마 구분, 예: token-stats,heading-consistency)",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="사용 가능한 검사 모듈 목록을 출력하고 종료",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _filter_registry(names: list[str] | None):
    """이름으로 체크를 필터링한 새 레지스트리 반환."""
    from md_doctor.checks import default_checks

    reg = default_checks()
    if names is None:
        return reg
    allowed = {n.strip() for n in names if n.strip()}
    reg.checks = [c for c in reg.checks if c.name in allowed]
    return reg


def _format_text(report, min_sev: Severity) -> str:
    lines: list[str] = []
    if not report.files:
        lines.append(f"📭 검사 대상 마크다운 파일이 없습니다 (스캔: {report.scanned_paths}).")
        return "\n".join(lines)

    lines.append(f"🔍 md-doctor v{__version__} — {report.total_files}개 파일 스캔")
    lines.append(
        f"   ❌ 오류 {report.total_errors}  ⚠️  경고 {report.total_warnings}  ℹ️  정보 {report.total_infos}"
    )
    lines.append("")

    threshold = min_sev.rank
    any_issue = False
    for fr in report.files:
        visible = [d for d in fr.diagnoses if d.severity.rank >= threshold]
        if not visible:
            continue
        any_issue = True
        lines.append(f"📄 {fr.path}")
        for d in visible:
            badge = _SEVERITY_BADGE[d.severity]
            loc = f":{d.line}" if d.line else ""
            rule = f" [{d.rule}]" if d.rule else ""
            lines.append(f"  {badge}{loc}{rule} {d.message}")
        lines.append("")

    if not any_issue:
        lines.append("✨ 표시할 이슈가 없습니다.")
    return "\n".join(lines)


def _format_json(report, min_sev: Severity) -> str:
    threshold = min_sev.rank
    payload = {
        "version": __version__,
        "summary": {
            "total_files": report.total_files,
            "errors": report.total_errors,
            "warnings": report.total_warnings,
            "infos": report.total_infos,
        },
        "files": [
            {
                "path": str(fr.path),
                "byte_size": fr.byte_size,
                "line_count": fr.line_count,
                "diagnoses": [
                    {
                        "check": d.check,
                        "rule": d.rule,
                        "severity": d.severity.value,
                        "line": d.line,
                        "message": d.message,
                    }
                    for d in fr.diagnoses
                    if d.severity.rank >= threshold
                ],
            }
            for fr in report.files
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _format_github(report, min_sev: Severity) -> str:
    """GitHub Actions 워크플로 명령어 출력."""
    threshold = min_sev.rank
    lines: list[str] = []
    for fr in report.files:
        for d in fr.diagnoses:
            if d.severity.rank < threshold:
                continue
            level = {"info": "notice", "warning": "warning", "error": "error"}[d.severity.value]
            file = str(fr.path)
            line = d.line or 1
            # 메시지에서 줄바꿈 → %0A
            msg = d.message.replace("\n", "%0A").replace("'", "''")
            lines.append(f"::{level} file={file},line={line}::{msg}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_checks:
        from md_doctor.checks import default_checks

        reg = default_checks()
        print("사용 가능한 검사 모듈:")
        for n in reg.names():
            print(f"  - {n}")
        return 0

    path: Path | None = args.path
    if path is None:
        print("❌ 경로를 지정해주세요. (도움말: md-doctor --help)", file=sys.stderr)
        return 2
    if not path.exists():
        print(f"❌ 경로가 존재하지 않습니다: {path}", file=sys.stderr)
        return 2

    min_sev = Severity(args.min_severity)
    fail_on = Severity(args.fail_on) if args.fail_on != "never" else None
    checks = args.checks.split(",") if args.checks else None
    registry = _filter_registry(checks)

    try:
        if path.is_dir():
            report = diagnose_tree(path, glob=args.glob, registry=registry)
        else:
            fr = diagnose_file(path, registry=registry)
            from md_doctor.models import DoctorReport

            report = DoctorReport(files=[fr], scanned_paths=[path])
    except MdDoctorError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    if args.format == "text":
        out = _format_text(report, min_sev)
    elif args.format == "json":
        out = _format_json(report, min_sev)
    else:  # github
        out = _format_github(report, min_sev)

    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    if fail_on is not None:
        threshold = fail_on.rank
        if any(d.severity.rank >= threshold for fr in report.files for d in fr.diagnoses):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
