#!/usr/bin/env python3
import logging

import argparse
import os
import sys

import pandas as pd

from sustainablecompetition.benchmarkatoms import Job, JobState, JobStateError, Result
from sustainablecompetition.methods.methodinterface import Benchmarker
from sustainablecompetition.infrastructureadapters.virtualrunner import VirtualRunner

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Test run the benchmarking tool")
    parser.add_argument("file", help="Path to CSV file containing solver runtimes")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    df = pd.read_csv(args.file, index_col="hash")
    runner = VirtualRunner(df)


if __name__ == "__main__":
    main()
