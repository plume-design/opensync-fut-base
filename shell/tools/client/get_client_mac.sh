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
tools/client/get_client_mac.sh [-h] arguments
Description:
    - Get mac address of client interface 'wlan0'
Arguments:
    -h  show this help message
    - \$1 (wlan_namespace) : Interface namespace name : (string)(required)
    - \$2 (interface_name) : Interface name           : (string)(required)
Script usage example:
    ./tools/client/get_client_mac.sh nswifi1 wlan0
    ./tools/client/get_client_mac.sh nseth351 eth0.351
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "tools/client/get_client_mac.sh" -arg

wlan_namespace=${1}
if_name=${2}

wlan_namespace_cmd="sudo ip netns exec ${wlan_namespace} bash"

mac_addr=$(${wlan_namespace_cmd} -c "ifconfig ${if_name}" | grep -i 'ether' | awk '{ print $2 }')
echo "$mac_addr"
