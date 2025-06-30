#!/bin/bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
check_traffic_to_client.sh [-h]
Description:
    This script checks if traffic is flowing to the IP/Port of the host.
    Note that, this function runs iperf3 client and host must be running
    iperf3 server to check traffic flow successfully.
Options:
    -h  show this help message
Arguments:
    wan_ip=$1   -- IP address of the host                   - (string)(required)
    port_num=$2 -- port number, the traffic is checked on   - (int)(required)
Script usage example:
    ./shell/tools/server/check_traffic_to_client.sh 192.168.200.10 5201
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "check_traffic_to_client.sh" -arg

wan_ip=${1}
port_num=${2}

log "check_traffic_to_client.sh: Checking if traffic is flowing to the IP and port address of the host"

check_traffic_iperf3_client $wan_ip $port_num

pass
