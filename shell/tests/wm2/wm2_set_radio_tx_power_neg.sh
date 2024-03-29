#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"
channel_change_timeout=60
usage()
{
cat << usage_string
wm2/wm2_set_radio_tx_power_neg.sh [-h] arguments
Description:
    - Make sure all radio interfaces for this device are up and have valid
      configuration. If not create new interface with configuration
      parameters from test case configuration.
    - Set tx_power to requested valid "tx_power" for creating interface.
    - Change tx_power to mismatch_tx_power. Update Wifi_Radio_Config table.
    - Check if mismatch_tx_power is applied to Wifi_Radio_State table. If applied
      test fails.
    - Check if mismatch_tx_power is applied to system. If applied test fails.
    - Check if WIRELESS MANAGER is still running.
Arguments:
    -h  show this help message
    (radio_idx)         : Wifi_VIF_Config::vif_radio_idx              : (int)(required)
    (if_name)           : Wifi_Radio_Config::if_name                  : (string)(required)
    (ssid)              : Wifi_VIF_Config::ssid                       : (string)(required)
    (channel)           : Wifi_Radio_Config::channel                  : (int)(required)
    (ht_mode)           : Wifi_Radio_Config::ht_mode                  : (string)(required)
    (hw_mode)           : Wifi_Radio_Config::hw_mode                  : (string)(required)
    (mode)              : Wifi_VIF_Config::mode                       : (string)(required)
    (vif_if_name)       : Wifi_VIF_Config::if_name                    : (string)(required)
    (tx_power)          : used as tx_power in Wifi_Radio_Config table : (int)(required)
    (mismatch_tx_power) : used as mismatch_tx_power                   : (int)(required)
    (channel_mode)      : Wifi_Radio_Config::channel_mode             : (string)(required)
    (enabled)           : Wifi_Radio_Config::enabled                  : (string)(required)
    (wpa)               : Wifi_VIF_Config::wpa                        : (string)(required)
    (wifi_security_type) : 'wpa' if wpa fields are used or 'legacy' if security fields are used: (string)(required)

Wifi Security arguments(choose one or the other):
    If 'wifi_security_type' == 'wpa' (preferred)
    (wpa_key_mgmt)      : Wifi_VIF_Config::wpa_key_mgmt               : (string)(required)
    (wpa_psks)          : Wifi_VIF_Config::wpa_psks                   : (string)(required)
    (wpa_oftags)        : Wifi_VIF_Config::wpa_oftags                 : (string)(required)
                    (OR)
    If 'wifi_security_type' == 'legacy' (deprecated)
    (security)          : Wifi_VIF_Config::security                   : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_radio_tx_power_neg.sh  -vif_radio_idx <VIF-RADIO-IDX> -if_name <IF_NAME> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT_MODE> -hw_mode <HW_MODE> -mode <MODE> -vif_if_name <VIF_IF_NAME> -tx_power <TX_POWER> -mismatch_tx_power <MISMATCH_TX_POWER> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
                        (OR)
                 Run: ./wm2/wm2_set_radio_tx_power_neg.sh  -vif_radio_idx <VIF-RADIO-IDX> -if_name <IF_NAME> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT_MODE> -hw_mode <HW_MODE> -mode <MODE> -vif_if_name <VIF_IF_NAME> -tx_power <TX_POWER> -mismatch_tx_power <MISMATCH_TX_POWER> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -security <SECURITY>
Script usage example:
    ./wm2/wm2_set_radio_tx_power_neg.sh -vif_radio_idx 2 -if_name wifi1 -ssid test_wifi_50L -channel 44 -ht_mode HT20 -hw_mode 11ac -mode ap -vif_if_name home-ap-l50 -tx_power 23 -mismatch_tx_power 25 -channel_mode manual -enabled "true" -wifi_security_type wpa -wpa -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
    ./wm2/wm2_set_radio_tx_power_neg.sh -vif_radio_idx 2 -if_name wifi1 -ssid test_wifi_50L -channel 44 -ht_mode HT20 -hw_mode 11ac -mode ap -vif_if_name home-ap-l50 -tx_power 23 -mismatch_tx_power 25 -channel_mode manual -enabled "true" -wifi_security_type legacy -security '["map",[["encryption","WPA-PSK"],["key","FutTestPSK"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=28
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_radio_tx_power_neg.sh" -arg

if [ $mismatch_tx_power -lt 1 ] && [ $mismatch_tx_power -gt 32 ]; then
    raise "$mismatch_tx_power is not between 1 and 32" -l "wm2/wm2_set_radio_tx_power_neg.sh" -s
fi

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
        -channel | \
        -vif_radio_idx)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -vif_if_name)
            vif_if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${vif_if_name}"
            shift
            ;;
        -if_name)
            if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${if_name}"
            shift
            ;;
        -mismatch_tx_power)
            mismatch_tx_power=${1}
            shift
            ;;
        -ht_mode | \
        -channel_mode | \
        -enabled)
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -tx_power)
            tx_power=${1}
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${tx_power}"
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
            [ "${wifi_security_type}" != "wpa" ] && raise "FAIL: Incorrect combination of WPA and legacy wifi security type provided" -l "wm2/wm2_set_radio_tx_power_neg.sh" -arg
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -security)
            [ "${wifi_security_type}" != "legacy" ] && raise "FAIL: Incorrect combination of WPA and legacy wifi security type provided" -l "wm2/wm2_set_radio_tx_power_neg.sh" -arg
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;

        *)
            raise "FAIL: Wrong option provided: $option" -l "wm2/wm2_set_radio_tx_power_neg.sh" -arg
            ;;
    esac
done
log_title "wm2/wm2_set_radio_tx_power_neg.sh: WM2 test - Testing Wifi_Radio_Config field mismatch_tx_power - '${mismatch_tx_power}'"

log "wm2/wm2_set_radio_tx_power_neg.sh: Checking if Radio/VIF states are valid for test"
check_radio_vif_state \
    ${radio_vif_args} &&
        log "wm2/wm2_set_radio_tx_power_neg.sh: Radio/VIF states are valid" ||
            (
                log "wm2/wm2_set_radio_tx_power_neg.sh: Cleaning VIF_Config"
                vif_reset
                log "wm2/wm2_set_radio_tx_power_neg.sh: Radio/VIF states are not valid, creating interface..."
                create_radio_vif_interface \
                    ${radio_vif_args} \
                    ${create_radio_vif_args} \
                    -timeout ${channel_change_timeout} \
                    -disable_cac &&
                        log "wm2/wm2_set_radio_tx_power_neg.sh: create_radio_vif_interface - Interface $if_name created - Success"
            ) ||
        raise "FAIL: create_radio_vif_interface - Interface $if_name not created" -l "wm2/wm2_set_radio_tx_power_neg.sh" -tc

log "wm2/wm2_set_radio_tx_power_neg.sh: Changing tx_power to $mismatch_tx_power"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u tx_power "$mismatch_tx_power" &&
    log "wm2/wm2_set_radio_tx_power_neg.sh: update_ovsdb_entry - Wifi_Radio_Config::tx_power is $mismatch_tx_power - Success" ||
    raise "FAIL: update_ovsdb_entry - Wifi_Radio_Config::tx_power is not $mismatch_tx_power" -l "wm2/wm2_set_radio_tx_power_neg.sh" -oe

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_power "$mismatch_tx_power" -t ${channel_change_timeout} &&
    raise "FAIL: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::tx_power is $mismatch_tx_power" -l "wm2/wm2_set_radio_tx_power_neg.sh" -ow ||
    log "wm2/wm2_set_radio_tx_power_neg.sh: wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::tx_power is not $mismatch_tx_power - Success"

# LEVEL2 check. Passes if system reports original tx_power is still set.
tx_power_from_os=$(get_tx_power_from_os "$vif_if_name") ||
    raise "FAIL: Error while fetching tx_power from system" -l "wm2/wm2_set_radio_tx_power_neg.sh" -fc

if [ "$tx_power_from_os" = "" ]; then
    raise "FAIL: Error while fetching tx_power from system" -l "wm2/wm2_set_radio_tx_power_neg.sh" -fc
else
    if [ "$tx_power_from_os" != "$mismatch_tx_power" ]; then
        log "wm2/wm2_set_radio_tx_power_neg.sh: tx_power '$mismatch_tx_power' not applied to system. System reports current tx_power '$tx_power_from_os' - Success"
    else
        raise "FAIL: tx_power '$mismatch_tx_power' applied to system. System reports current tx_power '$tx_power_from_os'" -l "wm2/wm2_set_radio_tx_power_neg.sh" -tc
    fi
fi

log "wm2/wm2_set_radio_tx_power_neg.sh: Reversing tx_power to normal value"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u tx_power "$tx_power" &&
    log "wm2/wm2_set_radio_tx_power_neg.sh: update_ovsdb_entry - Wifi_Radio_Config table updated - tx_power $tx_power" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Radio_Config - tx_power $tx_power" -l "wm2/wm2_set_radio_tx_power_neg.sh" -tc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is tx_power "$tx_power" -t ${channel_change_timeout} &&
    log "wm2/wm2_set_radio_tx_power_neg.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State - tx_power $tx_power" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State - tx_power $tx_power" -l "wm2/wm2_set_radio_tx_power_neg.sh" -tc

# Check if manager survived.
manager_bin_file="${OPENSYNC_ROOTDIR}/bin/$(get_wireless_manager_name)"
wait_for_function_response 0 "check_manager_alive $manager_bin_file" &&
    log "wm2/wm2_set_radio_tx_power_neg.sh: Success: WIRELESS MANAGER is running" ||
    raise "FAIL: WIRELESS MANAGER not running/crashed" -l "wm2/wm2_set_radio_tx_power_neg.sh" -tc

pass

