#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "$fut_topdir/lib/rpi_lib.sh"

help()
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

ARGS=""
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

help
exit 1
