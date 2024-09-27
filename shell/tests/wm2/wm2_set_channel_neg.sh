#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"
# Wait for channel to change, not necessarily become usable (CAC for DFS)
channel_change_timeout=60

usage()
{
cat << usage_string
wm2/wm2_set_channel_neg.sh [-h] arguments
Description:
    - Make sure all radio interfaces for this device are up and have valid
      configuration. If not create new interface with configuration parameters
      from test case configuration.
    - Set channel to requested "channel" value first.
    - Check for mismatch_channel is not allowed on the radio.
    - Change channel to mismatch_channel. Update Wifi_Radio_Config table.
    - Check if channel setting is applied to Wifi_Radio_State table. If applied test fails.
    - Check if channel setting is applied to system. If applied test fails.
    - Check if WIRELESS MANAGER is still running.
Arguments:
    -h  show this help message
    (radio_if_name)   : Wifi_Radio_Config::if_name        : (string)(required)
    (vif_if_name)     : Wifi_VIF_Config::if_name          : (string)(required)
    (vif_radio_idx)   : Wifi_VIF_Config::vif_radio_idx    : (int)(required)
    (ssid)            : Wifi_VIF_Config::ssid             : (string)(required)
    (channel)         : Wifi_Radio_Config::channel        : (int)(required)
    (ht_mode)         : Wifi_Radio_Config::ht_mode        : (string)(required)
    (hw_mode)         : Wifi_Radio_Config::hw_mode        : (string)(required)
    (mode)            : Wifi_VIF_Config::mode             : (string)(required)
    (mismatch_channel): mismatch channel to verify        : (int)(required)
    (channel_mode)    : Wifi_Radio_Config::channel_mode   : (string)(required)
    (enabled)         : Wifi_Radio_Config::enabled        : (string)(required)
    (wpa)             : Wifi_VIF_Config::wpa              : (string)(required)
    (wpa_key_mgmt)    : Wifi_VIF_Config::wpa_key_mgmt     : (string)(required)
    (wpa_psks)        : Wifi_VIF_Config::wpa_psks         : (string)(required)
    (wpa_oftags)      : Wifi_VIF_Config::wpa_oftags       : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_channel_neg.sh -radio_if_name <IF_NAME> -vif_if_name <VIF_IF_NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT_MODE> -hw_mode <HW_MODE> -mode <MODE> -mismatch_channel <MISMATCH_CHANNEL> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
Script usage example:
    ./wm2/wm2_set_channel_neg.sh -radio_if_name wifi2 -vif_if_name home-ap-u50 -vif_radio_idx 2 -ssid FUTssid -channel 108 -ht_mode HT40 -hw_mode 11ac -mode ap -mismatch_channel 180 -channel_mode manual -enabled "true"  -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=30
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_channel_neg.sh" -arg

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    print_tables Wifi_VIF_Config Wifi_VIF_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

# Parsing arguments passed to the script.
while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -mode | \
        -ssid | \
        -channel | \
        -hw_mode | \
        -vif_radio_idx)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -radio_if_name)
            radio_if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${radio_if_name}"
            shift
            ;;
        -vif_if_name)
            vif_if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${vif_if_name}"
            shift
            ;;
        -channel_mode | \
        -enabled | \
        -ht_mode)
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -mismatch_channel)
            mismatch_channel=${1}
            shift
            ;;
        -wpa | \
        -wpa_key_mgmt | \
        -wpa_psks | \
        -wpa_oftags)
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        *)
            raise "Wrong option provided: $option" -l "wm2/wm2_set_bcn_int.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_set_channel_neg.sh: WM2 test - Verify mismatching channels cannot be set - '${mismatch_channel}'"

log "wm2/wm2_set_channel_neg.sh: Checking if Radio/VIF states are valid for test"
check_radio_vif_state \
    ${radio_vif_args} &&
        log "wm2/wm2_set_channel_neg.sh: Radio/VIF states are valid" ||
            (
                log "wm2/wm2_set_channel_neg.sh: Radio/VIF states are not valid, creating interface..."
                create_radio_vif_interface \
                    ${radio_vif_args} \
                    ${create_radio_vif_args} \
                    -timeout ${channel_change_timeout} &&
                        log "wm2/wm2_set_channel_neg.sh: create_radio_vif_interface - Interface $radio_if_name created - Success"
            ) ||
        raise "create_radio_vif_interface - Interface $radio_if_name not created" -l "wm2/wm2_set_channel_neg.sh" -ds

# Check Wifi_Radio_State::allowed_channels is populated for tested VIF
wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_Radio_State allowed_channels -w if_name ${if_name}" &&
allowed_channels=$(get_ovsdb_entry_value Wifi_Radio_State allowed_channels -w if_name "$radio_if_name" -r)
echo "$allowed_channels" | grep -qwF "$mismatch_channel" &&
    raise "Radio $radio_if_name supports channel $mismatch_channel" -l "wm2/wm2_set_channel_neg.sh" -tc ||
    log "wm2/wm2_set_channel_neg.sh: Radio $radio_if_name does not support channel $mismatch_channel, continue execution"

# Update Wifi_Radio_Config with mismatched channel
update_ovsdb_entry Wifi_Radio_Config -w if_name $radio_if_name -u channel $mismatch_channel &&
    log "wm2/wm2_set_channel_neg.sh: update_ovsdb_entry - Wifi_Radio_Config::channel is $mismatch_channel - Success" ||
    raise "update_ovsdb_entry - Wifi_Radio_Config::channel is not $mismatch_channel" -l "wm2/wm2_set_channel_neg.sh" -fc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is channel "$mismatch_channel" -t ${channel_change_timeout} &&
    raise "wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::channel is $mismatch_channel" -l "wm2/wm2_set_channel_neg.sh" -tc ||
    log "wm2/wm2_set_channel_neg.sh: wait_ovsdb_entry - Wifi_Radio_Config is not reflected to Wifi_Radio_State::channel is not $mismatch_channel - Success"

# LEVEL2 check. Passes if system reports original channel is still set.
channel_from_os=$(get_channel_from_os $vif_if_name) ||
    raise "Error while fetching channel from system" -l "wm2/wm2_set_channel_neg.sh" -fc

if [ "$channel_from_os" = "" ]; then
    raise "Error while fetching channel from os" -l "wm2/wm2_set_channel_neg.sh" -fc
else
    if [ "$channel_from_os" != "$mismatch_channel" ]; then
        log "wm2/wm2_set_channel_neg.sh: Channel '$mismatch_channel' not applied to system. System reports current channel '$channel_from_os' - Success"
    else
        raise "Channel '$mismatch_channel' applied to system. System reports current channel '$channel_from_os" -l "wm2/wm2_set_channel_neg.sh" -tc
    fi
fi

pass
