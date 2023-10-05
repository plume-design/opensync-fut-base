#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh &> /dev/null
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "${fut_topdir}"/lib/unit_lib.sh &> /dev/null

usage() {
    cat << usage_string
tools/client/reboot_client.sh [-h] arguments
Description:
    - Reboot client device
Arguments:
    -h  show this help message
Script usage example:
    ./tools/client/reboot_client.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -lt ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "tools/client/reboot_client.sh" -arg

if [[ "$EUID" -ne 0 ]]; then
    raise "FAIL: Please run this function as root - sudo" -l "tools/client/reboot_client.sh"
fi

sleep 1 && reboot &
exit 0
