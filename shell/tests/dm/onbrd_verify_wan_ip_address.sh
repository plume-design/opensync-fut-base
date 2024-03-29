#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_wan_ip_address.sh [-h] arguments
Description:
    - Validate wan ip address
Arguments:
    -h  show this help message
    \$1 (wan_if_name)       : used as interface name to check WAN IP if WANO is disabled : (string)(required)
    \$2 (inet_addr)         : used as WAN IP address to be checked                       : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_wan_ip_address.sh <WAN-INTERFACE> <WAN-IP>
Script usage example:
    ./onbrd/onbrd_verify_wan_ip_address.sh eth0 192.168.200.10
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Inet_State
check_restore_ovsdb_server
ifconfig "$wan_if_name"
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_wan_ip_address.sh" -arg
wan_if_name=${1}
inet_addr=${2}

log_title "onbrd/onbrd_verify_wan_ip_address.sh: ONBRD test - Verify WAN_IP in Wifi_Inet_State is correctly applied"

log "onbrd/onbrd_verify_wan_ip_address.sh: Verify WAN IP address '$inet_addr' for interface '$wan_if_name'"
wait_ovsdb_entry Wifi_Inet_State -w if_name "$wan_if_name" -is inet_addr "$inet_addr" &&
    log "onbrd/onbrd_verify_wan_ip_address.sh: wait_ovsdb_entry - Wifi_Inet_State '$wan_if_name' inet_addr is equal to '$inet_addr' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Wifi_Inet_State '$wan_if_name' inet_addr is not equal to '$inet_addr'" -l "onbrd/onbrd_verify_wan_ip_address.sh" -tc

wait_for_function_response 0 "check_wan_ip_l2 $wan_if_name $inet_addr" &&
    log "onbrd/onbrd_verify_wan_ip_address.sh: LEVEL2 - WAN IP for '$wan_if_name' is equal to '$inet_addr' - Success" ||
    raise "FAIL: LEVEL2 - WAN IP for '$wan_if_name' is not equal to '$inet_addr'" -l "onbrd/onbrd_verify_wan_ip_address.sh" -tc

pass
