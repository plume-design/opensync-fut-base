#!/bin/sh

# Clean up after tests for WM.

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
wm/wm_cleanup.sh [-h] arguments
Description:
    - Script removes interface from Wifi_VIF_Config.
Arguments:
    -h : show this help message
    \$1 (if_name)    : used for interface name  : (string)(required)
Script usage example:
    ./wm/wm_cleanup.sh home-ap-l50
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wm/wm_cleanup.sh" -arg
if_name=${1}

log "wm/wm_cleanup.sh: Clean up interface ${if_name} from Wifi_VIF_Config"
remove_ovsdb_entry Wifi_VIF_Config -w if_name "${if_name}" &&
    log "wm/wm_cleanup.sh: OVSDB entry from Wifi_VIF_Config removed for $if_name - Success" ||
    log -err "wm/wm_cleanup.sh: Failed to remove OVSDB entry from Wifi_VIF_Config for $if_name"

wait_ovsdb_entry_remove Wifi_VIF_State -w if_name "${if_name}" &&
    log "wm/wm_cleanup.sh: OVSDB entry from Wifi_VIF_State removed for $if_name - Success" ||
    log -err "wm/wm_cleanup.sh: Failed to remove OVSDB entry from Wifi_VIF_State for $if_name"

print_tables Wifi_Inet_Config
print_tables Wifi_Inet_State
print_tables Wifi_VIF_Config
print_tables Wifi_VIF_State

pass
