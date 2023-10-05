#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"

def_association_timeout=10
usage()
{
cat << usage_string
wm2/wm2_verify_associated_clients.sh [-h] arguments
Description:
    - Script to verify Wifi_Associated_Clients table is populated with correct values when client is connected to DUT.
Arguments:
    -h  show this help message
    \$1 (vif_if_name)         : Wifi_VIF_Config::if_name                   : (string)(required)
    \$2 (mac_addr)            : MAC address of client connected to ap      : (string)(required)
    \$3 (association_timeout) : Time to wait for Client to be associated   : (string)(optional) : (default:${def_association_timeout})
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_verify_associated_clients.sh <IF-NAME> <CLIENT MAC>
Script usage example:
    ./wm2/wm2_verify_associated_clients.sh wl0.2 a1:b2:c3:d4:e5:f6

usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_info_dump_line
    print_tables Wifi_Associated_Clients
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument" -l "wm2/wm2_verify_associated_clients.sh" -arg
vif_if_name=${1}
mac_addr=${2}
association_timeout=${3:-$def_association_timeout}

log_title "wm2/wm2_verify_associated_clients.sh: WM2 test - Verify Wifi_Associated_Clients table is populated with client MAC"

wait_for_function_response 0 "${OVSH} s Wifi_Associated_Clients" ${association_timeout} &&
    log "wm2/wm2_verify_associated_clients.sh: Wifi_Associated_Clients table populated - Success" ||
    raise "FAIL: Wifi_Associated_Clients table not populated" -l "wm2/wm2_verify_associated_clients.sh" -tc

wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_VIF_State associated_clients -w if_name ${vif_if_name}" ${association_timeout} &&
    assoc_clients_res=$(get_ovsdb_entry_value Wifi_VIF_State associated_clients -w if_name "${vif_if_name}") ||
    raise "FAIL: Failed to retrieve client associated to VIF ${vif_if_name}" -l "wm2/wm2_verify_associated_clients.sh" -tc

wait_ovsdb_entry Wifi_Associated_Clients  -w _uuid "[\"uuid\",\"${assoc_clients_res}\"]" -is mac "${mac_addr}" -is state "active" -t ${association_timeout} &&
    log "wm2/wm2_verify_associated_clients.sh: check_ovsdb_entry - client '${mac_addr}' is  associated to ${vif_if_name} - Success" ||
    raise "FAIL: check_ovsdb_entry - client ${mac_addr} not associated to ${vif_if_name}" -l "wm2/wm2_verify_associated_clients.sh" -tc

pass
