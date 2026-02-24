#!/bin/bash

#SBATCH --job-name=parsl-main
#SBATCH --output=parsl-main-%j.log
#SBATCH --error=parsl-main-%j.log
#SBATCH --signal=B:USR1@300             # 5 min warning before end
#SBATCH --time=24:00:00                 # total walltime
#SBATCH --partition=cpuonly             # name of slurm partition to use for the main job
#SBATCH --nodes=1                       # only one node
#SBATCH --ntasks=1                      # single task (process)
#SBATCH --cpus-per-task=1               # single core

# Make sure to load the right modules from your environment
export PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1
source ./venv/bin/activate

# Using 'exec' is important for signal handling to work correctly, allowing the process to receive signals directly rather than through a shell intermediary. This ensures that the shutdown handler in the code can catch signals like SIGUSR1 sent by SLURM before job termination, enabling graceful shutdown and cleanup.
exec python ./src/dike.py ./config/satcomp25.yml --requeue "$SLURM_SUBMIT_DIR/satcomp25.slurm.sh"
