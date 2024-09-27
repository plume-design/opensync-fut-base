#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/othr_setup.sh"

usage()
{
cat << usage_string
othr/othr_verify_lan_bridge_iface_wifi_master_state.sh [-h] arguments
Description:
    - Verify Wifi_Master_State table exists and has LAN bridge interface populated.
Arguments:
    -h  show this help message
    \$1 (lan_bridge_if_name)     : LAN bridge interface to be checked : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./othr/othr_verify_lan_bridge_iface_wifi_master_state.sh <LAN_BRIDGE_IF_NAME>
Script usage example:
    ./othr/othr_verify_lan_bridge_iface_wifi_master_state.sh br-lan
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Master_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_verify_lan_bridge_iface_wifi_master_state.sh" -arg
lan_bridge_if_name=${1}

log_title "othr/othr_verify_lan_bridge_iface_wifi_master_state.sh: ONBRD test - Verify Wifi_Master_State table exists and has LAN bridge interface populated"

${OVSH} s Wifi_Master_State
if [ $? -eq 0 ]; then
    log "othr/othr_verify_lan_bridge_iface_wifi_master_state.sh: Wifi_Master_State table exists - Success"
else
    raise "Wifi_Master_State table does not exist" -l "othr/othr_verify_lan_bridge_iface_wifi_master_state.sh" -tc
fi

check_ovsdb_entry Wifi_Master_State -w if_name $lan_bridge_if_name
if [ $? -eq 0 ]; then
    log "othr/othr_verify_lan_bridge_iface_wifi_master_state.sh: Wifi_Master_State populated with LAN bridge interface '$lan_bridge_if_name' - Success"
else
    raise "Wifi_Master_State not populated with LAN bridge interface '$lan_bridge_if_name'" -l "othr/othr_verify_lan_bridge_iface_wifi_master_state.sh" -tc
fi

pass
