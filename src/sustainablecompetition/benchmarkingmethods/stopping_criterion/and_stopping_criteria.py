from sustainablecompetition.benchmarkatoms import Result
from sustainablecompetition.benchmarkingmethods.stopping_criterion.stopping_criteria import StoppingCriteria


__all__ = ["AndStoppingCriteria"]


class AndStoppingCriteria(StoppingCriteria):
    """
    Stops when anally of the stopping criterion is true.
    """

    def __init__(self, criteria: list[StoppingCriteria]):
        super().__init__()
        self.criteria: list[StoppingCriteria] = []
        for c in criteria:
            if isinstance(c, AndStoppingCriteria):
                self.criteria += c.criteria
            else:
                self.criteria.append(c)

    def should_stop(self) -> bool:
        return all(c.should_stop() for c in self.criteria)

    def handle_result(self, result: Result) -> None:
        for c in self.criteria:
            c.handle_result(result)
