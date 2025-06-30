#!/bin/bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
export FUT_TOPDIR=${fut_topdir}
source "${fut_topdir}/shell/lib/unit_lib.sh"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
stop_iperf3_server.sh [-h]
Description:
    This script stops the iperf3 server.
Arguments:
    -h  show this help message
Script usage example:
    ./shell/tools/server/stop_iperf3_server.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "stop_iperf3_server.sh: Stopping iperf3 server"

killall_process_by_name "iperf3"
