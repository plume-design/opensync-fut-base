#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
wm2/wm2_set_radio_tx_chainmask.sh [-h] arguments
Description:
    - Script tries to set chosen TX CHAINMASK values. Recommended values: 1, 3, 7, 15. Choose non-default values.
Arguments:
    -h  show this help message
    \$1 (if_name)               : Wifi_Radio_Config::if_name        : (string)(required)
    \$2 (freq_band)             : Wifi_Radio_Config::freq_band      : (string)(required)
    \$3 (test_tx_chainmask)     : Wifi_Radio_Config::tx_chainmask   : (int)(required)
    \$4 (max_tx_chainmask)      : Wifi_Radio_Config::tx_chainmask   : (int)(required)
    \$5 (default_tx_chainmask)  : Wifi_Radio_Config::tx_chainmask   : (int)(required)
Script usage example:
    ./wm2/wm2_set_radio_tx_chainmask.sh wifi1 5GU 3 15 7
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=5
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_radio_tx_chainmask.sh" -arg
if_name=${1}
freq_band=${2}
test_tx_chainmask=${3}
max_tx_chainmask=${4}
default_tx_chainmask=${5}

trap '
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    print_tables Wifi_VIF_Config Wifi_VIF_State
    fut_info_dump_line
' EXIT INT TERM

[ ${test_tx_chainmask} -le 0 ] &&
    raise "Invalid tx_chainmask:'$test_tx_chainmask', must be greater than zero" -l "wm2/wm2_set_radio_tx_chainmask.sh" -arg

[ ${max_tx_chainmask} -le 0 ] &&
    raise "Invalid tx_chainmask:'$max_tx_chainmask', must be greater than zero" -l "wm2/wm2_set_radio_tx_chainmask.sh" -arg

# Set TX chainmask to MAX value
log "wm2/wm2_set_radio_tx_chainmask.sh: Changing tx_chainmask to $max_tx_chainmask"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u tx_chainmask "$max_tx_chainmask" &&
    log "wm2/wm2_set_radio_tx_chainmask.sh: update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is $max_tx_chainmask - Success" ||
    raise "update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is not $max_tx_chainmask" -l "wm2/wm2_set_radio_tx_chainmask.sh" -fc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_chainmask "$max_tx_chainmask" &&
    log "wm2/wm2_set_radio_tx_chainmask.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::tx_chainmask is $max_tx_chainmask - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::tx_chainmask is not $max_tx_chainmask" -l "wm2/wm2_set_radio_tx_chainmask.sh" -tc

# Set TX chainmask to test value
log "wm2/wm2_set_radio_tx_chainmask.sh: Changing tx_chainmask to $test_tx_chainmask"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u tx_chainmask "$test_tx_chainmask" &&
    log "wm2/wm2_set_radio_tx_chainmask.sh: update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is $test_tx_chainmask - Success" ||
    raise "update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is not $test_tx_chainmask" -l "wm2/wm2_set_radio_tx_chainmask.sh" -fc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_chainmask "$test_tx_chainmask" &&
    log "wm2/wm2_set_radio_tx_chainmask.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::tx_chainmask is $test_tx_chainmask - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::tx_chainmask is not $test_tx_chainmask" -l "wm2/wm2_set_radio_tx_chainmask.sh" -tc

# Set TX chainmask to pre-test default value
log "wm2/wm2_set_radio_tx_chainmask.sh: Changing tx_chainmask to $default_tx_chainmask"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u tx_chainmask "$default_tx_chainmask" &&
    log "wm2/wm2_set_radio_tx_chainmask.sh: update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is $default_tx_chainmask - Success" ||
    raise "update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is not $default_tx_chainmask" -l "wm2/wm2_set_radio_tx_chainmask.sh" -fc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_chainmask "$default_tx_chainmask" &&
    log "wm2/wm2_set_radio_tx_chainmask.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::tx_chainmask is $default_tx_chainmask - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::tx_chainmask is not $default_tx_chainmask" -l "wm2/wm2_set_radio_tx_chainmask.sh" -tc

pass
