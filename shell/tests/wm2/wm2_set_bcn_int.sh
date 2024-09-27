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
wm2/wm2_set_bcn_int.sh [-h] arguments
Description:
    - Script tries to set chosen BEACON INTERVAL.
Arguments:
    -h  show this help message
    (radio_if_name) : Wifi_Radio_Config::if_name     : (string)(required)
    (vif_if_name)   : Wifi_VIF_Config::if_name       : (string)(required)
    (bcn_int)       : Wifi_Radio_Config::bcn_int     : (int)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_bcn_int.sh <RADIO-IF-NAME> <VIF-IF-NAME> <BCN_INT>

Script usage example:
    ./wm2/wm2_set_bcn_int.sh wifi1 b-ap-l50 200
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_bcn_int.sh" -arg

radio_if_name=${1}
vif_if_name=${2}
bcn_int=${3}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    print_tables Wifi_VIF_Config Wifi_VIF_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "wm2/wm2_set_bcn_int.sh: WM2 test - Testing Wifi_Radio_Config field bcn_int - '${bcn_int}'}"

log "wm2/wm2_set_bcn_int.sh: Changing bcn_int to $bcn_int"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" -u bcn_int "$bcn_int" &&
    log "wm2/wm2_set_bcn_int.sh: update_ovsdb_entry - Wifi_Radio_Config::bcn_int is $bcn_int - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Radio_Config::bcn_int is not $bcn_int" -l "wm2/wm2_set_bcn_int.sh" -fc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is bcn_int "$bcn_int" &&
    log "wm2/wm2_set_bcn_int.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::bcn_int is $bcn_int - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::bcn_int is not $bcn_int" -l "wm2/wm2_set_bcn_int.sh" -tc

log "wm2/wm2_set_bcn_int.sh: Checking BEACON INTERVAL set on system - LEVEL2"
check_beacon_interval_at_os_level "$bcn_int" "$vif_if_name" ||
    log "wm2/wm2_set_bcn_int.sh: LEVEL2 - check_beacon_interval_at_os_level - BEACON INTERVAL $bcn_int set on system - Success" ||
    raise "LEVEL2 - check_beacon_interval_at_os_level - BEACON INTERVAL $bcn_int not set on system" -l "wm2/wm2_set_bcn_int.sh" -tc

pass
