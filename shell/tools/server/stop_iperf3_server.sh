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
tools/server/stop_iperf3_server.sh [-h]
Description:
    This script stops the iperf3 server.
Arguments:
    -h  show this help message
Script usage example:
    ./tools/server/stop_iperf3_server.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "tools/server/stop_iperf3_server.sh: Stopping iperf3 server"

killall_process_by_name "iperf3"
