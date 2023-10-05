#!/usr/bin/env python3

import subprocess


if __name__ == "__main__":
    active_containers_cmd = 'docker container list --filter=ancestor=fut-server --format "{{.ID}}"'.split()

    active_containers = subprocess.Popen(
        active_containers_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = active_containers.communicate()
    container = stdout.decode("utf-8").strip().strip('"')

    if not container:
        print("No active containers were found")
        exit(0)

    print(f"Active containers:\n{container}")

    stop_containers_cmd = f"docker container stop {container}".split()

    stop_containers = subprocess.Popen(
        stop_containers_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = stop_containers.communicate()
    stdout = stdout.decode("utf-8").strip()
    exit_code = stop_containers.returncode

    print(f"Stopped containers:\n{stdout}")
    exit(exit_code)
