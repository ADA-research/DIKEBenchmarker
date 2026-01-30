"""Stopping criterion that stops when a minimum ranking accuracy is reached with a Wilcoxon test."""

import importlib
import warnings

from sustainablecompetition.benchmarkatoms import Result
from sustainablecompetition.benchmarkingmethods.stopping_criterion.stopping_criteria import StoppingCriteria
from sustainablecompetition.dataadaptors.sqlite_dataadaptor import SqlDataAdaptor

from scipy.stats import wilcoxon

__all__ = ["WilcoxonStoppingCriterion"]


class WilcoxonStoppingCriterion(StoppingCriteria):
    """Stopping criterion that stops when a minimum ranking accuracy is reached with a Wilcoxon test."""

    def __init__(self, benchmark_ids: list[str], solver_ids: list[str], min_accuracy: float, min_instances: int = 5):
        super().__init__()
        self.benchmark_ids = benchmark_ids
        self.min_accuracy = min_accuracy
        self.min_instances = min_instances
        self.selected_benchmark_ids = []
        db_path = importlib.resources.files("sustainablecompetition.data").joinpath("sustainablecompetition.db")
        self.db_adaptor = SqlDataAdaptor(db_path)
        self.solvers = solver_ids
        self.pairs = [(s1, s2) for i, s1 in enumerate(self.solvers) for s2 in self.solvers[i + 1 :]]

    def should_stop(self) -> bool:
        if len(self.selected_benchmark_ids) == 0 or len(self.selected_benchmark_ids) < self.min_instances:
            return False

        # Filter out benchmark instances where any solver has no performance data
        valid_benchmark_ids = []
        for benchmark_id in self.selected_benchmark_ids:
            all_have_perf = True
            for solver_id in self.solvers:
                perf_col = self.db_adaptor.get_performances(solver_hash=solver_id, inst_hash=benchmark_id).get_column("perf")
                if len(perf_col) == 0:
                    all_have_perf = False
                    break
            if all_have_perf:
                valid_benchmark_ids.append(benchmark_id)

        if len(valid_benchmark_ids) < self.min_instances:
            return False

        performances = {
            solver_id: [
                self.db_adaptor.get_performances(solver_hash=solver_id, inst_hash=benchmark_id).get_column("perf")[0] for benchmark_id in valid_benchmark_ids
            ]
            for solver_id in self.solvers
        }
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=UserWarning)
            undecided = []
            for s1, s2 in self.pairs:
                perf_i = performances[s1]
                perf_j = performances[s2]
                _, p_stop = wilcoxon(perf_i, perf_j, alternative="two-sided")
                current_confidence: float = 1 - p_stop
                if current_confidence < self.min_accuracy:
                    undecided.append((s1, s2))
            self.pairs = undecided

        return len(self.pairs) == 0

    def handle_result(self, result: Result) -> None:
        self.selected_benchmark_ids.append(result.job.benchmark_id)
