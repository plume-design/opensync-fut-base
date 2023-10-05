#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

topdir_path = Path(__file__).absolute().parents[1].as_posix()
sys.path.append(topdir_path)

usage_text = "python code_cov.py"
help_text = "Evaluate code coverage (by default, on 'framework' directory), using tests located in 'self_test/' directory. Requires 'pytest-cov' Python package."
parser = argparse.ArgumentParser(
    usage=usage_text,
    description=help_text,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("-c", "--cov", default="framework", help="Directory for which coverage check is evaluated.")
args = parser.parse_args()

subprocess.run(["python3", "-m", "pytest", "-s", f"--cov={topdir_path}/{str(args.cov)}", f"{topdir_path}/self_test/"])
