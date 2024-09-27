#!/bin/sh

# Clean up after tests for OTHR.

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
othr/othr_cleanup.sh [-h] arguments
Description:
    - Script removes interface from Wifi_Inet_Config and Wifi_VIF_Config,
      and removes interface from lan_bridge on DUT device
Arguments:
    -h : show this help message
    \$1 (lan_bridge) : used for LAN bridge name : (string)(required)
    \$2 (if_name)    : used for interface name  : (string)(required)
Script usage example:
    ./othr/othr_cleanup.sh br-home home-ap-l50
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_cleanup.sh" -arg
lan_bridge=${1}
if_name=${2}

log "othr/othr_cleanup.sh: Clean up interface ${if_name} from Wifi_Inet_Config"
remove_ovsdb_entry Wifi_Inet_Config -w if_name "${if_name}" &&
    log "othr/othr_cleanup.sh: OVSDB entry from Wifi_Inet_Config removed for $if_name - Success" ||
    log -err "othr/othr_cleanup.sh: Failed to remove OVSDB entry from Wifi_Inet_Config for $if_name"

wait_ovsdb_entry_remove Wifi_Inet_State -w if_name "${if_name}" &&
    log "othr/othr_cleanup.sh: OVSDB entry from Wifi_Inet_State removed for $if_name - Success" ||
    log -err "othr/othr_cleanup.sh: Failed to remove OVSDB entry from Wifi_Inet_State for $if_name"

remove_ovsdb_entry Wifi_VIF_Config -w if_name "${if_name}" &&
    log "othr/othr_cleanup.sh: OVSDB entry from Wifi_VIF_Config removed for $if_name - Success" ||
    log -err "othr/othr_cleanup.sh: Failed to remove OVSDB entry from Wifi_VIF_Config for $if_name"

log "othr/othr_cleanup.sh: Removing $if_name from bridge ${lan_bridge}"
remove_port_from_bridge "${lan_bridge}" "${if_name}" &&
    log "othr/othr_cleanup.sh: remove_port_from_bridge - port $if_name removed from $lan_bridge - Success" ||
    raise "remove_port_from_bridge - port $if_name NOT removed from $lan_bridge" -l "othr/othr_cleanup.sh" -tc

print_tables Wifi_Inet_Config
print_tables Wifi_Inet_State
print_tables Wifi_VIF_Config
print_tables Wifi_VIF_State

show_bridge_details

pass
