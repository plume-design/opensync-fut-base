#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${fut_topdir}"/lib/unit_lib.sh
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
    - \$3 (dut_ip_address)    : IP address of the DUT                                 : (string)(required)
    - \$4 (port)              : Port number on which upnpc is run                     : (int)(optional)(default=${def_port})

Script usage example:
    ./tools/client/run_upnp_client.sh nswifi1 10.10.10.20 10.10.10.30 5201
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/client/run_upnp_client.sh" -arg
wlan_namespace=${1}
client_ip_address=${2}
dut_ip_address=${3}
port=${4:-$def_port}
wlan_namespace_cmd="ip netns exec ${wlan_namespace} bash"

log_title "tools/client/run_upnp_client.sh: Run UPnP client on the device"

if [[ "$EUID" -ne 0 ]]; then
    raise "FAIL: Please run this function as root - sudo" -l "tools/client/run_upnp_client.sh"
fi

log "tools/client/run_upnp_client.sh: Adding default route on client"
${wlan_namespace_cmd} -c "ip route add default via ${dut_ip_address}"

log "tools/client/run_upnp_client.sh: Starting UPnPC on client host"
${wlan_namespace_cmd} -c "/usr/bin/upnpc -a ${client_ip_address} ${port} ${port} ${protocol}"
if [ $? -eq 0 ]; then
    log -deb "tools/client/run_upnp_client.sh: UPnP client started successfully on the device - Success"
else
    raise "FAIL: UPnP client failed to start on the device!" -l "tools/client/run_upnp_client.sh" -tc
fi

log "tools/client/run_upnp_client.sh: Running iperf server to check traffic"
${wlan_namespace_cmd} -c "nohup iperf3 -s -1 -D"

pass
