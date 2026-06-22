from __future__ import annotations

import argparse
from pathlib import Path

from core.scanner import Scanner
from reports.report_generator import MarkdownReportGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an authorised LLM application assessment.")
    parser.add_argument("--target", default="demo", help="Target name from config/targets.yaml. Default: demo")
    parser.add_argument("--profile", default="baseline", help="Assessment profile from config/attack_profiles.yaml. Default: baseline")
    parser.add_argument("--output", default="reports/output/scan-report.md", help="Markdown report output path.")
    parser.add_argument(
        "--authorised",
        action="store_true",
        help="Required for configured targets outside the demo mode. Use only where you have permission.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scanner = Scanner(config_dir=Path("config"))
    result = scanner.scan(target_name=args.target, profile_name=args.profile, authorised=args.authorised)
    output = MarkdownReportGenerator().generate(result, args.output)
    print(f"Assessment complete: {result.finding_count} findings. Report written to {output}")


if __name__ == "__main__":
    main()
