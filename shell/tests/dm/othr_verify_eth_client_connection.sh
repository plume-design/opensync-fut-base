#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
    cat <<usage_string
othr/othr_verify_eth_client_connection.sh [-h] arguments
Description:
    - Script verifies ETH client connection on DUT
Arguments:
    -h : show this help message
    \$1 (eth_if_name) : Interface name on which client should be connected : (string)(required)
    \$2 (client_mac)  : ETH client MAC address                             : (string)(required)
Script usage example:
    ./othr/othr_verify_eth_client_connection.sh eth1 dc:a6:32:c8:b1:5f
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables DHCP_leased_IP
    print_tables Connection_Manager_Uplink
    show_bridge_details
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
eth_if_name=${1}
client_mac=${2}

n_ping=3

log "othr/othr_verify_eth_client_connection.sh: Checking if has_L2==true and has_L3==false for ${eth_if_name} in Connection_Manager_Uplink table"
check_ovsdb_entry Connection_Manager_Uplink -w if_name "${eth_if_name}" -w has_L2 true -w has_L3 false &&
    log "othr/othr_verify_eth_client_connection.sh: has_L2==true and has_L3==false for ${eth_if_name} - Success" ||
    raise "Connection_Manager_Uplink table entry for ${eth_if_name} is not correct" -l "othr/othr_verify_eth_client_connection.sh" -tc

log "othr/othr_verify_eth_client_connection.sh: Checking if Client MAC address is present in DHCP_leased_IP"
check_ovsdb_entry DHCP_leased_IP -w hwaddr "${client_mac}" &&
    log "othr/othr_verify_eth_client_connection.sh: ETH Client MAC present in DHCP_leased_IP - Success" ||
    raise "ETH Client MAC address is not present in DHCP_leased_IP" -l "othr/othr_verify_eth_client_connection.sh" -tc

client_ip_address=$(get_ovsdb_entry_value DHCP_leased_IP inet_addr -w hwaddr "${client_mac}" -r)
log "othr/othr_verify_eth_client_connection.sh: Checking connectivity to ETH Client on ${client_ip_address}"
wait_for_function_response 0 "ping -c${n_ping} ${client_ip_address}" ${n_ping} &&
    log "othr/othr_verify_eth_client_connection.sh: ETH Client on ${client_ip_address} is pingable - Success" ||
    raise "ETH Client on ${client_ip_address} is not responding" -l "othr/othr_verify_eth_client_connection.sh" -tc

pass
