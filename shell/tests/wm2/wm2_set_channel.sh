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
wm2/wm2_set_channel.sh [-h] arguments
Description:
    - Script sets VIF to chosen channel. If interface is not UP it brings up the interface, checks if channel
      is allowed, and sets channel to desired value.
    - Check of channel is done in two levels: "Level1" test checks channel in Wifi_Radio_State table,
      "Level2" check verifies the system if the correct channel was applied.
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
    (channel_mode)    : Wifi_Radio_Config::channel_mode   : (string)(required)
    (enabled)         : Wifi_Radio_Config::enabled        : (string)(required)
    (wpa)              : Wifi_VIF_Config::wpa             : (string)(required)
    (wpa_key_mgmt)     : Wifi_VIF_Config::wpa_key_mgmt    : (string)(required)
    (wpa_psks)         : Wifi_VIF_Config::wpa_psks        : (string)(required)
    (wpa_oftags)       : Wifi_VIF_Config::wpa_oftags      : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_channel.sh -radio_if_name <IF_NAME> -vif_if_name <VIF_IF_NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT_MODE> -hw_mode <HW_MODE> -mode <MODE> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>

Script usage example:
    ./wm2/wm2_set_channel.sh -radio_if_name wifi2 -vif_if_name home-ap-u50 -vif_radio_idx 2 -ssid FUTssid -channel 128 -ht_mode HT40 -hw_mode 11ac -mode ap -channel_mode manual -enabled "true" -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=28
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_channel.sh" -arg

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
        -channel_mode | \
        -enabled | \
        -hw_mode | \
        -ht_mode | \
        -mode | \
        -ssid | \
        -vif_radio_idx)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -radio_if_name)
            radio_if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${radio_if_name}"
            shift
            ;;
        -channel)
            channel=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${channel}"
            shift
            ;;
        -vif_if_name)
            vif_if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${vif_if_name}"
            shift
            ;;
        -wpa | \
        -wpa_key_mgmt | \
        -wpa_psks | \
        -wpa_oftags)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        *)
            raise "Wrong option provided: $option" -l "wm2/wm2_set_channel.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_set_channel.sh: WM2 test - Testing Wifi_Radio_Config field channel - '${channel}'"

# Sanity check - is channel even allowed on the radio
check_is_channel_allowed "$channel" "$radio_if_name" &&
    log "wm2/wm2_set_channel.sh: check_is_channel_allowed - channel $channel is allowed on radio $radio_if_name" ||
    raise "Channel $channel is not allowed on radio $radio_if_name" -l "wm2/wm2_set_channel.sh" -ds

# Testcase:
# Configure radio, create VIF and apply channel
# This needs to be done simultaneously for the driver to bring up an active AP
log "wm2/wm2_set_channel.sh: Configuring Wifi_Radio_Config, creating interface in Wifi_VIF_Config."
log "wm2/wm2_set_channel.sh: Waiting for ${channel_change_timeout}s for settings {channel:$channel}"
create_radio_vif_interface \
    ${radio_vif_args} \
    -timeout ${channel_change_timeout} &&
        log "wm2/wm2_set_channel.sh: create_radio_vif_interface {$radio_if_name, $channel} - Success" ||
        raise "create_radio_vif_interface {$radio_if_name, $channel} - Interface not created" -l "wm2/wm2_set_channel.sh" -ds

log "wm2/wm2_set_channel.sh: Waiting for settings to apply to Wifi_Radio_State {channel:$channel}"
wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is channel "$channel" &&
    log "wm2/wm2_set_channel.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::channel is $channel - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::channel is not $channel" -l "wm2/wm2_set_channel.sh" -tc

log "wm2/wm2_set_channel.sh: Checking channel $channel at system level - LEVEL2"
check_channel_at_os_level "$channel" "$vif_if_name" &&
    log "wm2/wm2_set_channel.sh: check_channel_at_os_level - Channel $channel set at system level - Success" ||
    raise "check_channel_at_os_level - Channel $channel not set at system level" -l "wm2/wm2_set_channel.sh" -tc

pass
