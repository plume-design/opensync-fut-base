#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"
usage()
{
cat << usage_string
wm2/wm2_verify_associated_leaf.sh [-h] arguments
Description:
    - Script gets associated client from Wifi_VIF_State for the given interface and checks Wifi_Associated_Clients for leaf mac
Arguments:
    -h  show this help message
    \$1 (vif_if_name)   : Wifi_VIF_Config::if_name             : (string)(required)
    \$2 (mac_addr)      : leaf MAC address                     : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_verify_associated_leaf <VIF_IF_NAME> <MAC_ADDR>
Script usage example:
    ./wm2/wm2_verify_associated_leaf.sh wl1.1 84:1e:a3:89:87:53
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
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wm2/wm2_verify_associated_leaf.sh" -arg
vif_if_name=${1}
mac_addr=${2}

log_title "wm2/wm2_verify_associated_leaf.sh: WM2 test - Checks leaf $mac_addr is associated to $vif_if_name"

wait_for_function_response 0 "${OVSH} s Wifi_Associated_Clients" &&
    log "wm2/wm2_verify_associated_leaf.sh: Wifi_Associated_Clients table populated - Success" ||
    raise "FAIL: Wifi_Associated_Clients table not populated" -l "wm2/wm2_verify_associated_leaf.sh" -tc

wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_VIF_State associated_clients -w if_name ${vif_if_name}" &&
    assoc_leaf=$(get_ovsdb_entry_value Wifi_VIF_State associated_clients -w if_name "${vif_if_name}") ||
    raise "FAIL: Failed to retrieve leaf associated to ${vif_if_name}" -l "wm2/wm2_verify_associated_leaf.sh" -tc

check_ovsdb_entry Wifi_Associated_Clients  -w _uuid "[\"uuid\",\"${assoc_leaf}\"]"  -w mac "${mac_addr}" &&
    log "wm2/wm2_verify_associated_leaf.sh: check_ovsdb_entry - Leaf '${mac_addr}' is  associated to ${vif_if_name} - Success" ||
    raise "FAIL: check_ovsdb_entry - Leaf ${mac_addr} not associated to ${vif_if_name}" -l "wm2/wm2_verify_associated_leaf.sh" -tc

pass
