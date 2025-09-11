from sustainablecompetition.benchmarkatoms import Result
from sustainablecompetition.benchmarkingmethods.stopping_criterion.stopping_criteria import StoppingCriteria


__all__ = ["NoStoppingCriteria"]


class NoStoppingCriteria(StoppingCriteria):
    """
    Never stops
    """

    def should_stop(self) -> bool:
        return False

    def handle_result(self, result: Result) -> None:
        pass
