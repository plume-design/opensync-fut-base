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
othr/othr_verify_vif_iface_wifi_master_state.sh [-h] arguments
Description:
    - Verify Wifi_Master_State table exists and has VIF interface populated.
Arguments:
    -h  show this help message
    \$1 (vif_if_name)     : used as interface name to be checked : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./othr/othr_verify_vif_iface_wifi_master_state.sh <VIF_INTERFACE>
Script usage example:
    ./othr/othr_verify_vif_iface_wifi_master_state.sh bhaul-sta-24
    ./othr/othr_verify_vif_iface_wifi_master_state.sh bhaul-sta-l50
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
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_verify_vif_iface_wifi_master_state.sh" -arg
vif_if_name=${1}

log_title "othr/othr_verify_vif_iface_wifi_master_state.sh: ONBRD test - Verify Wifi_Master_State exists and has VIF interface '$vif_if_name' populated"

${OVSH} s Wifi_Master_State
if [ $? -eq 0 ]; then
    log "othr/othr_verify_vif_iface_wifi_master_state.sh: Wifi_Master_State table exists"
else
    raise "Wifi_Master_State table does not exist" -l "othr/othr_verify_vif_iface_wifi_master_state.sh" -tc
fi

wait_for_function_response 0 "check_ovsdb_entry Wifi_Master_State -w if_name $vif_if_name" &&
    log "othr/othr_verify_vif_iface_wifi_master_state.sh: Success: Wifi_Master_State populated with VIF interface '$vif_if_name'" ||
    raise "Wifi_Master_State not populated with VIF interface '$vif_if_name'" -l "othr/othr_verify_vif_iface_wifi_master_state.sh" -tc

pass

