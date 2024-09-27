#!/bin/bash

current_dir=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
export FUT_TOPDIR="$(realpath "$current_dir"/../../..)"

# FUT environment loading
source "${FUT_TOPDIR}/shell/config/default_shell.sh"
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
source "${FUT_TOPDIR}/shell/lib/rpi_lib.sh"


usage()
{
cat << usage_string
tools/server/run_iperf3_server.sh [-h]
Description:
    This script runs the iperf3 server to check traffic flow.
Arguments:
    -h  show this help message
    \$@ (port) : server port to listen on/connect to : (int)(optional)
Script usage example:
    ./tools/server/run_iperf3_server.sh
    ./tools/server/run_iperf3_server.sh 55687
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "tools/server/run_iperf3_server.sh: Running iperf3 server"

run_iperf3_server "$@"

pass
