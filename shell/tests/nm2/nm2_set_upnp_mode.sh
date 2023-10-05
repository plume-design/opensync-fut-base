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
nm2/nm2_set_upnp_mode.sh [-h] arguments
Description:
    - Script configures interfaces upnp through Wifi_inet_Config 'upnp_mode' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise

Arguments:
    -h  show this help message
    \$1 (wan_iface)       : Interface used for WAN uplink (WAN bridge or eth WAN) : (string)(required)
    \$2 (lan_bridge)      : Interface name of LAN bridge                          : (string)(required)
    \$3 (lan_ip_addr)     : IP address to be assigned on LAN interface            : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_upnp_mode.sh <WAN_IFACE> <BR-HOME> <IP-ADDR>
Script usage example:
    ./nm2/nm2_set_upnp_mode.sh eth0 br-home 10.10.10.30
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_upnp_mode.sh" -arg
wan_iface=${1}
lan_bridge=${2}
lan_ip_addr=${3}


trap '
fut_info_dump_line
check_pid_udhcp $wan_iface
print_tables Wifi_Inet_State
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_set_upnp_mode.sh: NM2 test - Setting UPnP mode"

# WAN bridge section
log "nm2/nm2_set_upnp_mode.sh: Setting Wifi_Inet_Config::ip_assign_scheme to dhcp on '$wan_iface'"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$wan_iface" -u ip_assign_scheme dhcp &&
    log "nm2/nm2_set_upnp_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::ip_assign_scheme is 'dhcp' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::ip_assign_scheme is not 'dhcp'" -l "nm2/nm2_set_upnp_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$wan_iface" -is ip_assign_scheme dhcp &&
    log "nm2/nm2_set_upnp_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::ip_assign_scheme is 'dhcp' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::ip_assign_scheme is not 'dhcp'" -l "nm2/nm2_set_upnp_mode.sh" -tc

log "nm2/nm2_set_upnp_mode.sh: Setting Wifi_Inet_Config::upnp_mode to external on '$wan_iface'"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$wan_iface" -u upnp_mode "external" &&
    log "nm2/nm2_set_upnp_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::upnp_mode is 'external' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::upnp_mode is not 'external'" -l "nm2/nm2_set_upnp_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$wan_iface" -is upnp_mode external &&
    log "nm2/nm2_set_upnp_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::upnp_mode is 'external' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::upnp_mode is not 'external'" -l "nm2/nm2_set_upnp_mode.sh" -tc

# LAN bridge section
update_ovsdb_entry Wifi_Inet_Config -w if_name "$lan_bridge" -u inet_addr ${lan_ip_addr} &&
    log "nm2/nm2_set_upnp_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::inet_addr is '${lan_ip_addr}' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::inet_addr is not '${lan_ip_addr}'" -l "nm2/nm2_set_upnp_mode.sh" -oe

update_ovsdb_entry Wifi_Inet_Config -w if_name "$lan_bridge" -u netmask 255.255.255.0 &&
    log "nm2/nm2_set_upnp_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::netmask is '255.255.255.0' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::netmask is not '255.255.255.0'" -l "nm2/nm2_set_upnp_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$lan_bridge" -is inet_addr ${lan_ip_addr} &&
    log "nm2/nm2_set_upnp_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::inet_addr is ${lan_ip_addr}  - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::inet_addr is not ${lan_ip_addr}" -l "nm2/nm2_set_upnp_mode.sh" -tc

wait_ovsdb_entry Wifi_Inet_State -w if_name "$lan_bridge" -is netmask 255.255.255.0 &&
    log "nm2/nm2_set_upnp_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::netmask is 255.255.255.0  - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::netmask is not 255.255.255.0" -l "nm2/nm2_set_upnp_mode.sh" -tc

log "nm2/nm2_set_upnp_mode.sh: Setting Wifi_Inet_Config::upnp_mode to internal on '$lan_bridge'"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$lan_bridge" -u upnp_mode "internal" &&
    log "nm2/nm2_set_upnp_mode.sh: update_ovsdb_entry - Wifi_Inet_Config::upnp_mode is 'internal' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::upnp_mode is not 'internal'" -l "nm2/nm2_set_upnp_mode.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$lan_bridge" -is upnp_mode internal &&
    log "nm2/nm2_set_upnp_mode.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::upnp_mode is 'internal' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::upnp_mode is not 'internal'" -l "nm2/nm2_set_upnp_mode.sh" -tc

print_tables Wifi_Inet_Config Wifi_Inet_State

pass
