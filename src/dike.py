#!/usr/bin/env python3

import argparse
import os
import sys
import yaml

from parsl.config import Config
from parsl import HighThroughputExecutor
from parsl.providers import LocalProvider

import polars as pl

from sustainablecompetition.infrastructureadaptors import slurm_limits

from sustainablecompetition.infrastructureadaptors.parsl_configs import make_slurm_config
from sustainablecompetition.infrastructureadaptors.parsl_runner import ParslRunner
from sustainablecompetition.benchmarkingmethods.trivial_benchmarker import TrivialBenchmarker
from sustainablecompetition.resultconsumers.lambda_consumer import LambdaConsumer
from sustainablecompetition.solveradaptors.executionwrapper import ExecutionWrapper
from sustainablecompetition.solveradaptors.solveradaptor import SolverAdaptor
from sustainablecompetition.benchmarkadaptors.satinstance import SATInstanceAdaptor
from sustainablecompetition.infrastructureadaptors import control


def get_solver_adaptor(solvers_csv: str) -> SolverAdaptor:
    """Create a SolverAdaptor from a CSV file."""
    solver_adaptor = SolverAdaptor()
    solver_adaptor.read_registry(solvers_csv)
    return solver_adaptor


def get_instance_adaptor() -> SATInstanceAdaptor:
    """Create a SATInstanceAdaptor with default paths."""
    instance_adaptor = SATInstanceAdaptor("./instances/sat/", "./instances/cnf_data.db")
    return instance_adaptor


def run_slurm(
    benchmarks,
    solvers,
    resource_limits,
    logroot,
    machine: str,
    account: str = None,
    tasks_per_node: int = 32,
    jobname: str = "benchmark",
    workerinit: str = "",
    queuelimit: int = None,
):
    """Run trivial benchmarking method on slurm cluster."""
    print(f"Benchmarking solvers in {solvers} using {len(benchmarks)} benchmarks")
    print(f"Using machine {machine} with account {account} and {tasks_per_node} tasks per node.")

    solver_adaptor = get_solver_adaptor(solvers)
    instance_adaptor = get_instance_adaptor()

    queue_max = queuelimit or slurm_limits.compute_max_blocks(safety_factor=0.8, fallback=100)

    config = make_slurm_config(
        partition=machine,
        account=account,
        jobname=jobname,
        tasks_per_node=tasks_per_node,
        walltime_seconds=resource_limits["solver_walltime"] + resource_limits["checker_walltime"],
        max_blocks=queue_max,
        worker_init=workerinit,
    )

    methods = []
    for sid in solver_adaptor.get_ids():
        method = TrivialBenchmarker(benchmarks, sid, checker_id=solver_adaptor.get_checker(sid), logroot=logroot)
        method.register_consumer(LambdaConsumer(print))
        methods.append(method)

    runner = ParslRunner(
        solver_adaptor=solver_adaptor,
        instance_adaptor=instance_adaptor,
        solver_wrapper=ExecutionWrapper(
            cputime=resource_limits["solver_cputime"], walltime=resource_limits["solver_walltime"], mem=resource_limits["solver_memory"]
        ),
        checker_wrapper=ExecutionWrapper(
            cputime=resource_limits["checker_cputime"], walltime=resource_limits["checker_walltime"], mem=resource_limits["checker_memory"]
        ),
        parsl_config=config,
    )

    runner.run(methods, njobs=queue_max * tasks_per_node)


def run_local(
    benchmarks,
    solvers,
    resource_limits,
    logroot,
    parallel: int = 3,
    jobname: str = "benchmark",
):
    """Run trivial benchmarking method on local machine."""
    print(f"Benchmarking solvers in {solvers} using {len(benchmarks)} benchmarks")
    print(f"Running locally with parallel={parallel} and jobname={jobname}")

    solver_adaptor = get_solver_adaptor(solvers)
    instance_adaptor = get_instance_adaptor()

    config = Config(executors=[HighThroughputExecutor(label=jobname, max_workers_per_node=parallel, provider=LocalProvider())])

    methods = []
    for sid in solver_adaptor.get_ids():
        method = TrivialBenchmarker(benchmarks, sid, checker_id=solver_adaptor.get_checker(sid), logroot=logroot)
        method.register_consumer(LambdaConsumer(print))
        methods.append(method)

    runner = ParslRunner(
        solver_adaptor=solver_adaptor,
        instance_adaptor=instance_adaptor,
        solver_wrapper=ExecutionWrapper(
            cputime=resource_limits["solver_cputime"], walltime=resource_limits["solver_walltime"], mem=resource_limits["solver_memory"]
        ),
        checker_wrapper=ExecutionWrapper(
            cputime=resource_limits["checker_cputime"], walltime=resource_limits["checker_walltime"], mem=resource_limits["checker_memory"]
        ),
        parsl_config=config,
    )

    runner.run(methods, njobs=parallel * 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DIKE: Data-Informed Knowledge-driven Evaluation")

    parser.add_argument("config", type=str, help="Path to YAML configuration file")
    parser.add_argument("--requeue", type=str, default=None, help="Path to slurm script for requeuing; if not provided then requeuing is disabled.")

    args = parser.parse_args()

    if args.requeue:
        control.set_slurm_requeue_script_path(args.requeue)

    # Load configuration from YAML file
    try:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML configuration: {e}")
        sys.exit(1)

    # Get the directory containing the config file
    config_dir = os.path.dirname(os.path.abspath(args.config))

    # Load benchmarks from CSV
    benchmarks_file = os.path.join(config_dir, config.get("benchmarks"))
    if not benchmarks_file or not os.path.isfile(benchmarks_file):
        print(f"Error: Benchmarks file '{benchmarks_file}' not found.")
        sys.exit(1)
    df = pl.read_csv(benchmarks_file)
    benchmarks = df.select("hash").to_series().to_list()

    # Load solvers file
    solvers_file = os.path.join(config_dir, config.get("solvers"))
    if not solvers_file or not os.path.isfile(solvers_file):
        print(f"Error: Solvers file '{solvers_file}' not found.")
        sys.exit(1)

    # Extract resource limits from configuration
    resource_limits = {
        "solver_cputime": config.get("solver_cputime", 5000),
        "solver_walltime": config.get("solver_walltime", 7000),
        "solver_memory": config.get("solver_memory", 64 * 1024),
        "checker_cputime": config.get("checker_cputime", 45000),
        "checker_walltime": config.get("checker_walltime", 70000),
        "checker_memory": config.get("checker_memory", 64 * 1024),
    }

    # Output directory for logs and results
    results = os.path.join(config_dir, config.get("results"))

    scheduling = config.get("scheduling", {})
    scheduler = scheduling.get("scheduler", "slurm")

    if scheduler == "slurm":
        print("Running with SLURM scheduler...")

        control.register_shutdown_handler()

        run_slurm(
            benchmarks=benchmarks,
            solvers=solvers_file,
            resource_limits=resource_limits,
            logroot=results,
            machine=scheduling.get("machine"),
            account=scheduling.get("account"),
            tasks_per_node=scheduling.get("tasks_per_node", 32),
            jobname=scheduling.get("jobname", "benchmark"),
            workerinit=scheduling.get("workerinit", ""),
            queuelimit=scheduling.get("queuelimit", None),
        )
    elif scheduler == "local":
        print("Running with local scheduler...")

        control.register_shutdown_handler()

        run_local(
            benchmarks=benchmarks,
            solvers=solvers_file,
            resource_limits=resource_limits,
            logroot=results,
            parallel=scheduling.get("parallel", 3),
            jobname=scheduling.get("jobname", "benchmark"),
        )
    else:
        print(f"Error: Unsupported scheduler '{scheduler}'.")
        sys.exit(1)
