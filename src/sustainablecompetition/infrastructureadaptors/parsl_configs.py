"""
Some basic Parsl configurations for demonstration and testing purposes.
"""

from parsl import ThreadPoolExecutor
from parsl.config import Config
from parsl.executors import HighThroughputExecutor

# needed by laptop config
from parsl.providers import LocalProvider
from parsl.addresses import address_by_hostname

# needed by slurm config
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher


def make_local_processes(n: int = 8) -> Config:
    """
    Launches a single block limited to $n processes with each worker using 1 core.
    """
    return Config(
        executors=[
            HighThroughputExecutor(
                label="local_processes",
                max_workers_per_node=n,
                provider=LocalProvider(init_blocks=1, min_blocks=n, max_blocks=1),
            )
        ]
    )


def make_local_threads(n: int = 8) -> Config:
    """
    Launches a single block limited to $n threads with each worker using 1 core.
    """
    return Config(
        executors=[ThreadPoolExecutor(label="local_threads", max_threads=n)],
        strategy=None,
    )


def make_slurm_config(
    partition: str = "compute",
    account: str | None = None,  # e.g., "your_allocation"
    nodes_per_block: int = 1,
    cores_per_node: int = 32,  # set to your node’s core count
    mem_per_node: int | None = None,  # in MB; or leave None to skip
    init_blocks: int = 0,  # start with zero and grow
    min_blocks: int = 0,
    max_blocks: int = 10,
    walltime: str = "02:00:00",
    worker_init: str = """
# Load your environment here:
module purge
module load python/3.11
# If using conda/mamba:
# source ~/miniconda3/etc/profile.d/conda.sh
# conda activate your-parsl-env
""".strip(),
) -> Config:
    """
    SLURM config that scales from 0..max_blocks blocks.
    Each block is an allocation of `nodes_per_block` nodes;
    on each node Parsl will start multiple workers.
    """
    scheduler_opts = []
    if account:
        scheduler_opts.append(f"#SBATCH --account={account}")
    if mem_per_node:
        scheduler_opts.append(f"#SBATCH --mem={mem_per_node}")

    return Config(
        executors=[
            HighThroughputExecutor(
                label="slurm_htex",
                address=address_by_hostname(),
                # Worker layout on each node:
                cores_per_worker=1,  # one worker per core by default
                max_workers=cores_per_node,  # cap per node
                worker_debug=True,
                provider=SlurmProvider(
                    partition=partition,
                    nodes_per_block=nodes_per_block,
                    init_blocks=init_blocks,
                    min_blocks=min_blocks,
                    max_blocks=max_blocks,
                    walltime=walltime,
                    launcher=SrunLauncher(overrides=""),  # use srun to launch
                    worker_init=worker_init,
                    scheduler_options="\n".join(scheduler_opts),
                    cmd_timeout=120,
                ),
            )
        ],
        strategy="simple",  # allow Parsl to scale blocks up/down
    )


# Example usage:
# import parsl
# cfg = make_slurm_config(
#     partition="cpu",
#     account="project_xy",
#     cores_per_node=64,
#     max_blocks=20,
#     walltime="04:00:00",
#     worker_init=\"""\
# module purge
# module load python/3.11 gcc/12.2 openmpi/4.1
# source ~/miniconda3/etc/profile.d/conda.sh
# conda activate parsl-env
# \""",
# )
# parsl.load(cfg)
