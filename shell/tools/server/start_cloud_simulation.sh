#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
Usage: ${MY_NAME} [--help|-h] [--stop|-s]

OPTIONS:
  --help|-h : this help message
  --stop|-s : stop the service instead of starting it

Script configures and (re)starts haproxy that acts as simulated cloud.
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

if [[ $# -eq 0 ]]; then
    start_cloud_simulation
    exit
fi

# parse command line arguments
while [[ "${1}" == -* ]]; do
    option="${1}"
    shift
    case "${option}" in
        -s | --stop)
            stop_cloud_simulation
            exit
            ;;
        -r | --restart)
            stop_cloud_simulation && start_cloud_simulation
            exit
            ;;
    esac
done

usage
exit 1
