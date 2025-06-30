#!/bin/bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
run_iperf3_server.sh [-h]
Description:
    This script runs the iperf3 server to check traffic flow.
Arguments:
    -h  show this help message
    \$@ (port) : server port to listen on/connect to : (int)(optional)
Script usage example:
    ./shell/tools/server/run_iperf3_server.sh
    ./shell/tools/server/run_iperf3_server.sh 55687
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "run_iperf3_server.sh: Running iperf3 server"

run_iperf3_server "$@"

pass
