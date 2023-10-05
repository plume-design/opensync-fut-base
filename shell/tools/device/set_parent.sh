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
cat << usage_string
tools/device/set_parent.sh [-h] arguments
Description:
    - Script updates the 'parent' field in Wifi_VIF_Config with the provided MAC address to ensure the
      connection with the correct parent node
Arguments:
    -h  show this help message
    \$1  (if_name)     : Wifi_VIF_Config::if_name : (string)(required)
    \$2  (mac_address) : LEAF MAC address         : (string)(required)
Script usage example:
    ./tools/device/set_parent.sh wl0 12:1e:a3:89:87:0d
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_ec=$?
fut_info_dump_line
if [ $fut_ec -ne 0 ]; then
    print_tables Wifi_VIF_Config Wifi_VIF_State
    check_restore_ovsdb_server
fi
fut_info_dump_line
exit $fut_ec
' EXIT SIGINT SIGTERM

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/device/set_parent.sh" -arg
if_name=${1}
mac_address=${2}

log_title "tools/device/set_parent.sh: Updating Wifi_VIF_Config::parent to $mac_address"

update_ovsdb_entry Wifi_VIF_Config -w if_name "$if_name" -u parent "$mac_address" &&
    log "tools/device/set_parent.sh: update_ovsdb_entry - Wifi_VIF_Config::parent is $mac_address - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_VIF_Config::parent is not $mac_address" -l "tools/device/set_parent.sh" -tc

wait_ovsdb_entry Wifi_VIF_State -w if_name "$if_name" -is parent "$mac_address" &&
    log "tools/device/set_parent.sh: wait_ovsdb_entry - Wifi_VIF_Config reflected to Wifi_VIF_State::parent is $mac_address - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_VIF_Config to Wifi_VIF_State::parent is not $mac_address" -l "tools/device/set_parent.sh" -tc

pass

