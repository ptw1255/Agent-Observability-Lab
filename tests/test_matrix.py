import json

from agent_observability_lab.matrix import run_matrix


def test_matrix_runs_every_pair_and_writes_aggregate(tmp_path):
    aggregate = run_matrix(tmp_path / "matrix", repetitions=1)

    assert aggregate["task_condition_runs"] == 15
    assert aggregate["profiled_runs"] == 45
    assert len(aggregate["summaries"]) == 15
    assert json.loads((tmp_path / "matrix" / "aggregate.json").read_text())["profiled_runs"] == 45
