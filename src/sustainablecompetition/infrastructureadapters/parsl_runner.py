"""
PARSL Runner Adapter
"""

from sustainablecompetition.infrastructureadapters.abstractrunner import AbstractRunner
from sustainablecompetition.benchmarkatoms import Job, Result
from sustainablecompetition.dataadapters.dataadapter import DataAdapter


class ParslRunner(AbstractRunner):
    """
    Simulate a runner using given runtimes dataset.
    """

    def __init__(self, runtimes: DataAdapter):
        super().__init__()
        self.runtimes = runtimes

    def submit(self, job: Job):
        """
        Submit a function to the process pool.
        Return an id for identification of the process future.
        """
        super().submit(job)
        # submit a job to a parsl executor here
        # and store the future in a list of futures
        # store the index of the future in job.external_id
        # TODO: write an actual job running function that can be submitted to parsl
        # The job running function will need to take the solver path and instance path as arguments
        # For the job running function to work, we need the runsolver binary to be available in the parsl execution environment
        # Write the code to checkout and build runsolver to be able to use it as a wrapper for the solver
        job.external_id = len(self.jobs) - 1
        job.mark_running()

    def completed(self, job: Job) -> Result:
        """
        Return the runtime result for the solver/instance pair.
        """
        extid = job.external_id
        job = self.jobs[extid]
        instance = job.benchmark_id
        solver = job.solver_id
        # Check if the parsl future is done here
        # If done, get the result and mark the job as finished or failed
        # The result consists of the solver output files which contain the runtime, result, status, etc.
        runtime = self.runtimes.get_performances(instance, solver).item()
        job.set_finished()
        return Result(job, runtime, 0)

    def cancel(self, job):
        return super().cancel(job)
