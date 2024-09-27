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
wm2/wm2_wds_backhaul_traffic_capture.sh [-h] arguments
Description:
    - Script validates the existence of 4-address frames being sent between
      the GW and LEAF devices in the process of establishing a WDS connection.
    - This shell script requires a plain-text file containing the parsed packet
      output captured using the tcpdump tool.
    - The 4-address frames should contain the following MAC addresses:
        - receiver address
        - destination address
        - transmitter address
        - source address
Arguments:
    -h  show this help message
    \$1  (ra)          : receiver MAC address                                 : (string)(required)
    \$2  (da)          : destination MAC address                              : (string)(required)
    \$3  (ta)          : transmitter MAC address                              : (string)(required)
    \$4  (sa)          : source MAC address                                   : (string)(required)
    \$4  (packet_file) : path to the file containing the parsed packet output : (string)(required)
Testcase procedure:

usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=5
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "wm2/wm2_wds_backhaul_traffic_capture.sh" -arg
ra=${1}
da=${2}
ta=${3}
sa=${4}
packet_file=${5}

log_title "wm2/wm2_wds_backhaul_traffic_capture.sh: WM2 test - Verifying the existence of 4-address WDS frames"

# Check if the file exists
if [ ! -e "$packet_file" ]; then
    raise "$packet_file does not exist." -l "wm2/wm2_wds_backhaul_traffic_capture.sh" -tc
fi

# Parse the file for the existence of the 4-address WDS frame
grep "RA:$ra TA:$ta DA:$da SA:$sa" "$packet_file"

if [ $? -ne 0 ]; then
    raise "The packet capture file does not contain the 4-address WDS frame." -l "wm2/wm2_wds_backhaul_traffic_capture.sh" -tc
fi

pass
