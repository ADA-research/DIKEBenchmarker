"""Stopping Criteria Interfaces"""

from abc import ABC, abstractmethod

from sustainablecompetition.benchmarkatoms import Result


__all__ = ["StoppingCriteria", "OrStoppingCriteria", "NoStoppingCriteria", "AndStoppingCriteria"]


class StoppingCriteria(ABC):
    """
    Decides when to stop submitting jobs.
    """

    @abstractmethod
    def should_stop(self) -> bool:
        """
        Return true if and only if the benchmarker has enough data to conclude
        """
        raise NotImplementedError

    @abstractmethod
    def handle_result(self, result: Result) -> None:
        """Called for each finished/failed job to update planning or process results."""
        raise NotImplementedError

    def __or__(self, value: "StoppingCriteria") -> "OrStoppingCriteria":
        return OrStoppingCriteria([self, value])

    def __and__(self, value: "StoppingCriteria") -> "AndStoppingCriteria":
        return AndStoppingCriteria([self, value])


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


class NoStoppingCriteria(StoppingCriteria):
    """
    Never stops
    """

    def should_stop(self) -> bool:
        return False

    def handle_result(self, result: Result) -> None:
        pass


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
