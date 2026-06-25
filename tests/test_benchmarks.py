from __future__ import annotations

from benchmarks.run_benchmarks import run_benchmarks, write_result


def test_fixture_benchmarks_execute(tmp_path) -> None:
    result = run_benchmarks(output_dir=tmp_path / "reports")

    assert result.status in {"pass", "fail"}
    assert result.benchmark_count == 3
    assert len(result.results) == 3
    assert all(item.report_path for item in result.results)


def test_benchmark_summary_written(tmp_path) -> None:
    result = run_benchmarks(output_dir=tmp_path / "reports")
    output = write_result(result, tmp_path / "summary.json")

    assert output.exists()
    assert "benchmark_count" in output.read_text(encoding="utf-8")
