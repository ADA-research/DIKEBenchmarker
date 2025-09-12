from sustainablecompetition.benchmarkatoms import Result
from sustainablecompetition.benchmarkingmethods.stopping_criterion.stopping_criteria import StoppingCriteria


__all__ = ["OrStoppingCriteria"]


class OrStoppingCriteria(StoppingCriteria):
    """
    Stops when any of the stopping criterion is true.
    """

    def __init__(self, criteria: list[StoppingCriteria]):
        super().__init__()
        self.criteria: list[StoppingCriteria] = []
        for c in criteria:
            if isinstance(c, OrStoppingCriteria):
                self.criteria += c.criteria
            else:
                self.criteria.append(c)

    def should_stop(self) -> bool:
        return any(c.should_stop() for c in self.criteria)

    def handle_result(self, result: Result) -> None:
        for c in self.criteria:
            c.handle_result(result)
