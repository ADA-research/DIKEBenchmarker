from typing import Iterator
from abc import ABC, abstractmethod

from benchmarkatoms import Job, Result


class Benchmarker(ABC):
    """Decides which jobs to submit next; can depend on past results/dependencies."""
    @abstractmethod
    def next_job(self) -> Job:
        """Return the next job to submit (can be None if no job is ready)."""
        raise NotImplementedError

    @abstractmethod
    def handle_result(self, result: Result) -> None:
        """Called for each finished/failed job to update planning or process results."""
        raise NotImplementedError


class Infrastructure(ABC):
    """
    Adapter to execution environment (cluster, SLURM, K8s, cloud API, vendor queue).
    """
    @abstractmethod
    def submit(self, job: Job):
        """Submit a job to the external system."""
        raise NotImplementedError

    @abstractmethod
    def completions(self) -> Iterator[Result]:
        """
        Must yield whenever the external system reports a job as done/failed.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel(self, job: Job):
        """Best-effort cancellation if supported by the external system."""
        return False


