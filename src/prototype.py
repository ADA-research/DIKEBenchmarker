#!/usr/bin/env python3
import logging

import argparse
import os
import sys

import polars as pl

from sustainablecompetition.controller import Controller
from sustainablecompetition.infrastructureadapters.virtualrunner import VirtualRunner
from sustainablecompetition.benchmarkingmethods.trivialbenchmarker import TrivialBenchmarker

logger = logging.getLogger(__name__)


def main():
    """
    Integration test using the trivial benchmarker (which submits all the instances)
    and the virtual runner (which returns the data from a csv file).
    """
    parser = argparse.ArgumentParser(description="Test run the benchmarking tool")
    parser.add_argument("file", help="Path to CSV file containing solver runtimes")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    df = pl.read_csv(args.file, index_col="hash")
    runner = VirtualRunner(df)
    benchmarks = df.select("hash").to_series().to_list()
    columns = df.columns.tolist()
    method = TrivialBenchmarker(benchmarks, columns[0])
    controller = Controller(method, runner, njobs=1)


if __name__ == "__main__":
    main()
