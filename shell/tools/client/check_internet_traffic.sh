#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}"/shell/lib/base_lib.sh

def_n_ping=5
def_ip="1.1.1.1"
usage()
{
cat << usage_string
tools/client/check_internet_traffic.sh [-h] arguments
Description:
    - Script checks device internet connectivity is blocked/unblocked with ping tool
Dependency:
    - "ping" tool with "-c" option to specify number of packets sent
Arguments:
    -h                        : Show this help message
    - \$1 (wlan_namespace)    : Interface namespace name                                    : (string)(required)
    - \$2 (traffic_state)     : 'block' to block internet, 'unblock' to unblock internet    : (string)(required)
    - \$3 (n_ping)            : How many packets are sent                                   : (int)(optional)(default=${def_n_ping})
    - \$4 (internet_check_ip) : IP address to validate internet connectivity                : (string)(optional)(default=${def_ip})
Script usage example:
    ./tools/client/check_internet_traffic.sh nswifi1 block
    ./tools/client/check_internet_traffic.sh nswifi1 unblock 10 1.1.1.1
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/client/check_internet_traffic.sh" -arg
wlan_namespace=${1}
traffic_state=${2}
n_ping=${3:-$def_n_ping}
internet_check_ip=${4:-$def_ip}

wlan_namespace_cmd="sudo ip netns exec ${wlan_namespace} bash"

log "tools/client/check_internet_traffic.sh: Verify if internet traffic is ${traffic_state}ed"

if ${wlan_namespace_cmd} -c "ping -c${n_ping} ${internet_check_ip}"; then
    if [ "$traffic_state" == "block" ]; then
        raise "Internet traffic is not blocked" -l "tools/client/check_internet_traffic.sh" -tc
    fi
else
    if [ "$traffic_state" == "unblock" ]; then
        raise "Internet traffic is not unblocked" -l "tools/client/check_internet_traffic.sh" -tc
    fi
fi

log "tools/client/check_internet_traffic.sh: Internet traffic is ${traffic_state}ed"

pass
