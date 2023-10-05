#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="nm2/nm2_setup.sh"

usage()
{
cat << usage_string
nm2/nm2_verify_router_mode.sh [-h] arguments
Description:
    - Validate device router mode settings, which checks:
        - if DHCP client running on WAN bridge
        - if NAT is enabled on WAN interface
        - if IP assignment scheme set as static for LAN interface
        - if NAT is disabled on LAN interface

Arguments:
    -h  show this help message
    \$1 (wan_iface)       : Interface used for WAN uplink (WAN bridge or eth WAN) : (string)(required)
    \$2 (lan_bridge)      : Interface name of LAN bridge                          : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_verify_router_mode.sh <WAN_IFACE> <BR-HOME>
Script usage example:
    ./nm2/nm2_verify_router_mode.sh eth0 br-home
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_verify_router_mode.sh" -arg
wan_iface=${1}
lan_bridge=${2}
dhcp_start_pool="10.10.10.20"
dhcp_end_pool="10.10.10.50"


trap '
fut_info_dump_line
check_pid_udhcp $wan_iface
print_tables Wifi_Inet_State
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_verify_router_mode.sh: ONBRD test - Verify router mode settings applied"

# WAN bridge section
log "nm2/nm2_verify_router_mode.sh: Check if interface '$wan_iface' is UP"
wait_for_function_response 0 "check_eth_interface_state_is_up $wan_iface" &&
    log "nm2/nm2_verify_router_mode.sh: Interface '$wan_iface' is UP - Success" ||
    raise "FAIL: Interface '$wan_iface' is DOWN, should be UP" -l "nm2/nm2_verify_router_mode.sh" -ds

# Check if DHCP client is running on WAN bridge
log "nm2/nm2_verify_router_mode.sh: Check if DHCP client is running on WAN bridge - '$wan_iface'"
wait_for_function_response 0 "check_pid_udhcp $wan_iface" &&
    log "nm2/nm2_verify_router_mode.sh: check_pid_udhcp '$wan_iface' - PID found, DHCP client running - Success" ||
    raise "FAIL: check_pid_udhcp '$wan_iface' - PID not found, DHCP client is not running" -l "nm2/nm2_verify_router_mode.sh" -tc

log "nm2/nm2_verify_router_mode.sh: Setting Wifi_Inet_Config::NAT to true on '$wan_iface'"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$wan_iface" -u NAT true &&
    log "nm2/nm2_verify_router_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::NAT is 'true' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::NAT is not 'true'" -l "nm2/nm2_verify_router_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$wan_iface" -is NAT true &&
    log "nm2/nm2_verify_router_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::NAT is 'true' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::NAT is not 'true'" -l "nm2/nm2_verify_router_mode.sh" -tc

# LAN bridge section
log "nm2/nm2_verify_router_mode.sh: Setting DHCP range on $lan_bridge to '$dhcp_start_pool' '$dhcp_end_pool'"
configure_dhcp_server_on_interface "$lan_bridge" "$dhcp_start_pool" "$dhcp_end_pool" &&
    log "nm2/nm2_verify_router_mode.sh: configure_dhcp_server_on_interface - DHCP settings updated - Success" ||
    raise "FAIL: Cannot update DHCP settings inside CONFIG $wan_iface" -l "nm2/nm2_verify_router_mode.sh" -tc

log "nm2/nm2_verify_router_mode.sh: Setting Wifi_Inet_Config::NAT to false"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$lan_bridge" -u NAT false &&
    log "nm2/nm2_verify_router_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::NAT is 'false' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::NAT is not 'false'" -l "nm2/nm2_verify_router_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$lan_bridge" -is NAT false &&
    log "nm2/nm2_verify_router_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::NAT is 'false' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::NAT is not 'false'" -l "nm2/nm2_verify_router_mode.sh" -tc

update_ovsdb_entry Wifi_Inet_Config -w if_name "$lan_bridge" -u ip_assign_scheme static &&
    log "nm2/nm2_verify_router_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::ip_assign_scheme is 'static' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::ip_assign_scheme is not 'static'" -l "nm2/nm2_verify_router_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$lan_bridge" -is ip_assign_scheme static &&
    log "nm2/nm2_verify_router_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::ip_assign_scheme is 'static' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::ip_assign_scheme is not 'static'" -l "nm2/nm2_verify_router_mode.sh" -tc

print_tables Wifi_Inet_Config Wifi_Inet_State

pass
