#!/usr/bin/env python3

import subprocess
import sys


def main():
    nodes = ",".join(sys.argv[1:]) if len(sys.argv) > 1 else "all"
    stream = subprocess.Popen(
        ["osrt", "pod", "wait", "--timeout", "300", nodes],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = stream.communicate()
    stdout = stdout.decode("utf-8").strip()
    exit_code = stream.returncode
    print(f"POD AVAILABILITY STATUS:\n{stdout}")
    exit(exit_code)


if __name__ == "__main__":
    main()
