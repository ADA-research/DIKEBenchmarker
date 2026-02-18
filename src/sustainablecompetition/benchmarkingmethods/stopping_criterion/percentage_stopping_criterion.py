"""Stopping criterion that stops after a given percentage of instances have been run."""

from sustainablecompetition.benchmarkatoms import Result
from sustainablecompetition.benchmarkingmethods.stopping_criterion.stopping_criteria import StoppingCriteria

__all__ = ["PercentageStoppingCriterion"]


class PercentageStoppingCriterion(StoppingCriteria):
    """Stopping criterion that stops after a given percentage of all benchmark instances have been run."""

    def __init__(self, benchmark_ids: list[str], percentage: float):
        super().__init__()
        self.benchmark_ids = benchmark_ids
        self.percentage = percentage
        self.selected_benchmark_ids: list[str] = []

    def should_stop(self) -> bool:
        if len(self.benchmark_ids) == 0:
            return True
        return len(self.selected_benchmark_ids) / len(self.benchmark_ids) >= self.percentage

    def handle_result(self, result: Result) -> None:
        self.selected_benchmark_ids.append(result.job.benchmark_id)
