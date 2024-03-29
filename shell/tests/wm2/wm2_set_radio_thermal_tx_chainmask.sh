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
wm2/wm2_set_radio_thermal_tx_chainmask.sh [-h] arguments
Description:
    - Script tries to set chosen THERMAL TX CHAINMASK. If interface is not UP it brings up the interface, and tries to set
      THERMAL TX CHAINMASK to desired value. Recomended values: 1, 3, 7, 15. Choose non-default values.
      THERMAL TX CHAINMASK is related to TX CHAINMASK - the device will combine the two chainmasks by performing
      AND operation on each bit of the chainmask. Test will enforce thermal_tx_chainmask < tx_chainmask.
Arguments:
    -h  show this help message
    (if_name)              : Wifi_Radio_Config::if_name              : (string)(required)
    (vif_if_name)          : Wifi_VIF_Config::if_name                : (string)(required)
    (vif_radio_idx)        : Wifi_VIF_Config::vif_radio_idx          : (int)(required)
    (ssid)                 : Wifi_VIF_Config::ssid                   : (string)(required)
    (channel)              : Wifi_Radio_Config::channel              : (int)(required)
    (ht_mode)              : Wifi_Radio_Config::ht_mode              : (string)(required)
    (hw_mode)              : Wifi_Radio_Config::hw_mode              : (string)(required)
    (mode)                 : Wifi_VIF_Config::mode                   : (string)(required)
    (tx_chainmask)         : Wifi_Radio_Config::tx_chainmask         : (int)(required)
    (thermal_tx_chainmask) : Wifi_Radio_Config::thermal_tx_chainmask : (int)(required)
    (freq_band)            : Wifi_Radio_Config::freq_band            : (string)(required)
    (channel_mode)         : Wifi_Radio_Config::channel_mode         : (string)(required)
    (enabled)              : Wifi_Radio_Config::enabled              : (string)(required)
    (wifi_security_type) : 'wpa' if wpa fields are used or 'legacy' if security fields are used: (string)(required)

Wifi Security arguments(choose one or the other):
    If 'wifi_security_type' == 'wpa' (preferred)
    (wpa)                  : Wifi_VIF_Config::wpa                    : (string)(required)
    (wpa_key_mgmt)         : Wifi_VIF_Config::wpa_key_mgmt           : (string)(required)
    (wpa_psks)             : Wifi_VIF_Config::wpa_psks               : (string)(required)
    (wpa_oftags)           : Wifi_VIF_Config::wpa_oftags             : (string)(required)
                    (OR)
    If 'wifi_security_type' == 'legacy' (deprecated)
    (security)             : Wifi_VIF_Config::security               : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_radio_thermal_tx_chainmask.sh -if_name <IF-NAME> -vif_if_name <VIF-IF-NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT-MODE> -hw_mode <HW-MODE> -mode <MODE> -tx_chainmask <TX_CHAINMASK> -thermal_tx_chainmask <THERMAL_TX_CHAINMASK> -radio_band <FREQ_BAND> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
                        (OR)
                 Run: ./wm2/wm2_set_radio_thermal_tx_chainmask.sh -if_name <IF-NAME> -vif_if_name <VIF-IF-NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT-MODE> -hw_mode <HW-MODE> -mode <MODE> -tx_chainmask <TX_CHAINMASK> -thermal_tx_chainmask <THERMAL_TX_CHAINMASK> -radio_band <FREQ_BAND> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -security <SECURITY>
Script usage example:
    ./wm2/wm2_set_radio_thermal_tx_chainmask.sh -if_name wifi1 -vif_if_name home-ap-l50 -vif_radio_idx 2 -ssid FUTssid -channel 36 -ht_mode HT20 -hw_mode 11ac -mode ap -tx_chainmask 15 -thermal_tx_chainmask 7 -radio_band 5GL -channel_mode manual -enabled "true" -wifi_security_type wpa -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'

usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=30
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg

trap '
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    print_tables Wifi_VIF_Config Wifi_VIF_State
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

# Parsing arguments passed to the script.
while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -hw_mode | \
        -mode | \
        -ssid | \
        -ht_mode | \
        -channel | \
        -vif_if_name | \
        -vif_radio_idx)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -if_name)
            if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${if_name}"
            shift
            ;;
        -channel_mode | \
        -enabled)
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -tx_chainmask)
            tx_chainmask=${1}
            shift
            ;;
        -thermal_tx_chainmask)
            thermal_tx_chainmask=${1}
            shift
            ;;
        -radio_band)
            freq_band=${1}
            shift
            ;;
        -wifi_security_type)
            wifi_security_type=${1}
            shift
            ;;
        -wpa | \
        -wpa_key_mgmt | \
        -wpa_psks | \
        -wpa_oftags)
            [ "${wifi_security_type}" != "wpa" ] && raise "FAIL: Incorrect combination of WPA and legacy wifi security type provided" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -security)
            [ "${wifi_security_type}" != "legacy" ] && raise "FAIL: Incorrect combination of WPA and legacy wifi security type provided" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        *)
            raise "FAIL: Wrong option provided: $option" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_set_radio_thermal_tx_chainmask.sh: WM2 test - Testing Wifi_Radio_Config field thermal_tx_chainmask"

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Enforce both thermal_tx_chainmask and tx_chainmask are greater than zero"
actual_tx_chainmask=$(get_actual_chainmask $tx_chainmask $freq_band)
[ ${actual_tx_chainmask} -le 0 ] &&
    raise "FAIL: Invalid tx_chainmask:'$actual_tx_chainmask', must be greater than zero" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg

actual_thermal_tx_chainmask=$(get_actual_chainmask $thermal_tx_chainmask $freq_band)
[ ${actual_thermal_tx_chainmask} -le 0 ] &&
    raise "FAIL: Invalid thermal_tx_chainmask:'$actual_thermal_tx_chainmask', must be greater than zero" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Enforce thermal_tx_chainmask < tx_chainmask"
if [ "$actual_thermal_tx_chainmask" -gt "$actual_tx_chainmask" ]; then
    raise "FAIL: Value of thermal_tx_chainmask '$actual_thermal_tx_chainmask' must be smaller than tx_chainmask '$actual_tx_chainmask'" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -arg
else
    value_to_check=$actual_thermal_tx_chainmask
fi

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Checking if Radio/VIF states are valid for test"
check_radio_vif_state \
    ${radio_vif_args} &&
        log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Radio/VIF states are valid" ||
            (
                log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Cleaning VIF_Config"
                vif_reset
                log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Radio/VIF states are not valid, creating interface..."
                create_radio_vif_interface \
                    ${radio_vif_args} \
                    ${create_radio_vif_args} \
                    -disable_cac &&
                        log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: create_radio_vif_interface - Interface $if_name created - Success"
            ) ||
        raise "FAIL: create_radio_vif_interface - Interface $if_name not created" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -ds

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Changing tx_chainmask to $actual_tx_chainmask"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u tx_chainmask "$actual_tx_chainmask" &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is $actual_tx_chainmask - Success" ||
    raise "FAIL: update_ovsdb_entry - Wifi_Radio_Config::tx_chainmask is not $actual_tx_chainmask" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -oe

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_chainmask "$actual_tx_chainmask" &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::tx_chainmask is $actual_tx_chainmask - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::tx_chainmask is not $actual_tx_chainmask" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -ds

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Checking TX CHAINMASK $actual_tx_chainmask at system level - LEVEL2"
check_tx_chainmask_at_os_level "$actual_tx_chainmask" "$if_name" &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: LEVEL2 - check_tx_chainmask_at_os_level - TX CHAINMASK $actual_tx_chainmask set at system level - Success" ||
    raise "FAIL: LEVEL2 - check_tx_chainmask_at_os_level - TX CHAINMASK $actual_tx_chainmask not set at system level" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -ds

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Changing thermal_tx_chainmask to $actual_thermal_tx_chainmask"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u thermal_tx_chainmask "$actual_thermal_tx_chainmask" &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: update_ovsdb_entry - Wifi_Radio_Config::thermal_tx_chainmask is $actual_thermal_tx_chainmask- Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Radio_Config::thermal_tx_chainmask is not $actual_thermal_tx_chainmask" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -oe

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Check if tx_chainmask changed to $value_to_check"
wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_chainmask "$value_to_check" &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::tx_chainmask is $value_to_check - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::tx_chainmask is not $value_to_check" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -tc

log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: Checking TX CHAINMASK $value_to_check at system level - LEVEL2"
check_tx_chainmask_at_os_level "$value_to_check" "$if_name" &&
    log "wm2/wm2_set_radio_thermal_tx_chainmask.sh: LEVEL2 - check_tx_chainmask_at_os_level - TX CHAINMASK $value_to_check set at system level - Success" ||
    raise "FAIL: LEVEL2 - check_tx_chainmask_at_os_level - TX CHAINMASK $value_to_check is not set at system" -l "wm2/wm2_set_radio_thermal_tx_chainmask.sh" -tc

pass
