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
wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh [-h] arguments
Description:
    - Script tries to set chosen THERMAL TX CHAINMASK back to default pre-test values (empty set).
Arguments:
    -h  show this help message
    \$1 (if_name)               : Wifi_Radio_Config::if_name        : (string)(required)
Script usage example:
    ./wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh wifi0

usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh" -arg
if_name=${1}

trap '
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    print_tables Wifi_VIF_Config Wifi_VIF_State
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u thermal_tx_chainmask '["set",[]]' &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh: update_ovsdb_entry - Wifi_Radio_Config::thermal_tx_chainmask is '[\"set\",[]]' - Success" ||
    raise "FAIL: update_ovsdb_entry - Wifi_Radio_Config::thermal_tx_chainmask is not '[\"set\",[]]'" -l "wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh" -oe

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is thermal_tx_chainmask '["set",[]]' &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::thermal_tx_chainmask is '[\"set\",[]]' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::thermal_tx_chainmask is not '[\"set\",[]]'" -l "wm2/wm2_set_radio_thermal_tx_chainmask_cleanup.sh" -tc
