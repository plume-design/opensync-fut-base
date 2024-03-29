#!/bin/sh

# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh > /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh > /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" > /dev/null

usage()
{
cat << usage_string
tools/device/retrieve_ping_packet_loss.sh [-h]
Description:
    - Script checks the ping statistics file for any packet loss.
Arguments:
    -h  show this help message
    \$1 (ping_log_file) : File containing the ping statistics : (string)(required)
Script usage example:
    ./tools/device/retrieve_ping_packet_loss.sh ping.log
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument" -l "tools/device/retrieve_ping_packet_loss.sh" -arg

ping_log_file=${1}

# Search for any non-zero packet loss in the PING log file

grep -E "([1-9][0-9]{0,2})% packet loss" "$ping_log_file" &&
    raise "FAIL: Packet loss detected" -l "tools/device/retrieve_ping_packet_loss.sh" -oe

log "tools/device/retrieve_ping_packet_loss.sh: No packet loss detected - Success"

pass
