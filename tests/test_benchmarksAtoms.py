import pytest
from datetime import datetime
from sustainablecompetition.benchmarkatoms import Job, JobState, JobStateError

class TestJob:
    @pytest.mark.asyncio
    async def test_set_finished_success():
        # Setup
        job = Job()
        job.state = JobState.RUNNING

        # Action
        await job.set_finished()

        # Assert
        assert job.state == JobState.FINISHED
        assert job.finished_at is not None
        assert isinstance(job.finished_at, datetime)

    @pytest.mark.asyncio
    async def test_set_finished_fails_if_not_running():
        # Setup
        job = Job()
        job.state = JobState.PENDING

        # Action & Assert
        with pytest.raises(JobStateError):
            await job.set_finished()