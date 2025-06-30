#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}"/shell/lib/base_lib.sh
def_port=5201
protocol="TCP"

usage() {
    cat << usage_string
tools/client/run_upnp_client.sh [-h] arguments
Description:
    - Run UPnP Client on the client device and run iperf3 server for traffic check.
Arguments:
    -h                        : Show this help message
    - \$1 (wlan_namespace)    : Interface namespace name                              : (string)(required)
    - \$2 (client_ip_address) : IP address to be assigned for the client interface    : (string)(required)
    - \$3 (port)              : Port number on which upnpc is run                     : (int)(optional)(default=${def_port})

Script usage example:
    ./tools/client/run_upnp_client.sh nswifi1 10.10.10.20 10.10.10.30 5201
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/client/run_upnp_client.sh" -arg
wlan_namespace=${1}
client_ip_address=${2}
port=${3:-$def_port}
wlan_namespace_cmd="ip netns exec ${wlan_namespace} bash"

trap '
    fut_ec=$?
    trap - EXIT INT
    [ -e /tmp/miniupnpd/mupnp_wan.leases ] && cat /tmp/miniupnpd/mupnp_wan.leases
    ps aux | grep iperf3 || true
    exit $fut_ec
' EXIT INT TERM

log_title "tools/client/run_upnp_client.sh: Run UPnP client on the device"

if [[ "$EUID" -ne 0 ]]; then
    raise "Please run this function as root - sudo" -l "tools/client/run_upnp_client.sh"
fi

log "tools/client/run_upnp_client.sh: Starting UPnPC on client host"
${wlan_namespace_cmd} -c "/usr/bin/upnpc -a ${client_ip_address} ${port} ${port} ${protocol}" &&
    log -deb "tools/client/run_upnp_client.sh: UPnP client started successfully on the device - Success" ||
    raise "UPnP client failed to start on the device!" -l "tools/client/run_upnp_client.sh" -tc

log "tools/client/run_upnp_client.sh: Running iperf server to check traffic"
${wlan_namespace_cmd} -c "nohup iperf3 -s -1 -D"

pass
