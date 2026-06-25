from __future__ import annotations

import json
from pathlib import Path

from scripts.run_functional_test import run_functional_test


def test_functional_acceptance_runner_generates_outputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "functional-test"

    summary = run_functional_test(output_dir=output_dir)

    assert summary.status == "pass"
    assert summary.target == ""
    assert summary.profile == ""
    assert not summary.errors

    summary_path = output_dir / "functional-test-summary.json"
    assert summary_path.exists()
    summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_data["status"] == "pass"
    assert summary_data["checks"]["targets_config_loaded"] == "pass"
    assert summary_data["checks"]["unknown_target_rejection"] == "pass"

    for generated_file in summary.generated_files:
        assert Path(generated_file).exists()
