#!/usr/bin/env python3

import subprocess


def main():
    stream = subprocess.Popen(["pod", "all", "wait", "timeout=300"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = stream.communicate()
    stdout = stdout.decode("utf-8").strip()
    exit_code = stream.returncode
    print(f"POD AVAILABILITY STATUS:\n{stdout}")
    exit(exit_code)


if __name__ == "__main__":
    main()
