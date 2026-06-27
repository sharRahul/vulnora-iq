from __future__ import annotations

from scripts.run_scan import build_parser


def test_targets_list_subcommand_does_not_require_root_target() -> None:
    args = build_parser().parse_args(["targets", "list"])

    assert args.command == "targets"
    assert args.targets_command == "list"
    assert args.target is None


def test_jobs_list_subcommand_does_not_require_root_target() -> None:
    args = build_parser().parse_args(["jobs", "list"])

    assert args.command == "jobs"
    assert args.jobs_command == "list"
    assert args.target is None


def test_direct_scan_mode_still_accepts_root_target_flags() -> None:
    args = build_parser().parse_args(["--target", "demo", "--authorised"])

    assert args.command is None
    assert args.target == "demo"
    assert args.authorised is True
