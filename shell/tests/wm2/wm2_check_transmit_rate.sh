#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${fut_topdir}"/lib/unit_lib.sh

usage()
{
cat << usage_string
wm2/wm2_check_transmit_rate.sh [-h] arguments
Description:
    - Script validates the data transmit rate on the device.
    - This shell script requires a plain-text file containing the parsed packet
      output captured using the tcpdump tool.
Arguments:
    -h  show this help message
    \$1 (transmit_rate) : the desired transmit rate in Mbps                    : (str)(required)
    \$1 (source_mac)    : source MAC address                                   : (str)(required)
    \$2 (packet_file)   : path to the file containing the parsed packet output : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./wm2/wm2_check_transmit_rate.sh 5.5 beacon_frames.txt
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "wm2/wm2_check_transmit_rate.sh" -arg
transmit_rate=${1}
source_mac=${2}
packet_file=${3}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "wm2/wm2_check_transmit_rate.sh: Verifying the the data transmit rate for $source_mac"

# Check if the file exists
if [ ! -e "$packet_file" ]; then
    raise "$packet_file does not exist." -l "wm2/wm2_wds_backhaul_traffic_capture.sh" -tc
fi

# Parse the file for specified transmit rate and source MAC address
awk "/$transmit_rate Mb/ && /SA:$source_mac Beacon/" "$packet_file" | grep .

if [ $? -ne 0 ]; then
    raise "The packet capture file does not contain the specified data transmit rate: $transmit_rate." -l "wm2/wm2_check_transmit_rate.sh" -tc
fi

pass
