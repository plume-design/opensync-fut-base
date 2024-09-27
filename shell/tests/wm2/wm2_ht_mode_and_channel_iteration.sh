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
channel_change_timeout=75

usage()
{
cat << usage_string
wm2/wm2_ht_mode_and_channel_iteration.sh [-h] arguments
Description:
    - Script configures radio in Wifi_Radio_Config, creates interface in
      Wifi_VIF_Config table and checks if settings are reflected in tables
      Wifi_Radio_State and Wifi_VIF_State.
      The script waits for the channel change for ${channel_change_timeout}s.
      Even if the channel is set in Wifi_Radio_State, it is not necessarily
      available for immediate use if CAC is in progress for DFS channels, but
      this is not under test in this script.
      Script fails if ht_mode fails to reflect to Wifi_Radio_State.
      Script fails if channel fails to reflect to Wifi_VIF_State.
Arguments:
    -h  show this help message
    (radio_if_name) : Wifi_Radio_Config::if_name        : (string)(required)
    (vif_if_name)   : Wifi_VIF_Config::if_name          : (string)(required)
    (vif_radio_idx) : Wifi_VIF_Config::vif_radio_idx    : (int)(required)
    (ssid)          : Wifi_VIF_Config::ssid             : (string)(required)
    (channel)       : Wifi_Radio_Config::channel        : (int)(required)
    (ht_mode)       : Wifi_Radio_Config::ht_mode        : (string)(required)
    (hw_mode)       : Wifi_Radio_Config::hw_mode        : (string)(required)
    (mode)          : Wifi_VIF_Config::mode             : (string)(required)
    (channel_mode)  : Wifi_Radio_Config::channel_mode   : (string)(required)
    (enabled)       : Wifi_Radio_Config::enabled        : (string)(required)
    (wpa)           : Wifi_VIF_Config::wpa              : (string)(required)
    (wpa_key_mgmt)  : Wifi_VIF_Config::wpa_key_mgmt     : (string)(required)
    (wpa_psks)      : Wifi_VIF_Config::wpa_psks         : (string)(required)
    (wpa_oftags)    : Wifi_VIF_Config::wpa_oftags       : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_ht_mode_and_channel_iteration.sh -radio_if_name <IF_NAME> -vif_if_name <VIF_IF_NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT_MODE> -hw_mode <HW_MODE> -mode <MODE> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
Script usage example:
    ./wm2/wm2_ht_mode_and_channel_iteration.sh -radio_if_name wifi1 -vif_if_name home-ap-l50 -vif_radio_idx 2 -ssid FUTssid -channel 36 -ht_mode HT20 -hw_mode 11ac -mode ap -channel_mode manual -enabled "true"  -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=28
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_ht_mode_and_channel_iteration.sh" -arg

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
        -ht_mode)
            ht_mode=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${ht_mode}"
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
            raise "Wrong option provided: $option" -l "wm2/wm2_ht_mode_and_channel_iteration.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_ht_mode_and_channel_iteration.sh: WM2 test - HT Mode and Channel Iteration - '${ht_mode}'-'${channel}'"

# Sanity check - is channel even allowed on the radio
check_is_channel_allowed "$channel" "$radio_if_name" &&
    log "wm2/wm2_ht_mode_and_channel_iteration.sh:check_is_channel_allowed - channel $channel is allowed on radio $radio_if_name" ||
    raise "Channel $channel is not allowed on radio $radio_if_name" -l "wm2/wm2_ht_mode_and_channel_iteration.sh" -ds

# Testcase:
# Configure radio, create VIF and apply ht_mode and channel
# This needs to be done simultaneously for the driver to bring up an active AP
log "wm2/wm2_ht_mode_and_channel_iteration.sh: Configuring Wifi_Radio_Config, creating interface in Wifi_VIF_Config."
log "wm2/wm2_ht_mode_and_channel_iteration.sh: Waiting for ${channel_change_timeout}s for settings {ht_mode:$ht_mode, channel:$channel}"
create_radio_vif_interface \
    ${radio_vif_args} \
    -timeout ${channel_change_timeout} &&
        log "wm2/wm2_ht_mode_and_channel_iteration.sh: create_radio_vif_interface {$radio_if_name, $ht_mode, $channel} - Interface $radio_if_name created - Success" ||
        raise "create_radio_vif_interface {$radio_if_name, $ht_mode, $channel} - Interface $radio_if_name not created" -l "wm2/wm2_ht_mode_and_channel_iteration.sh" -tc

log "wm2/wm2_ht_mode_and_channel_iteration.sh: Waiting for settings to apply to Wifi_Radio_State {channel:$channel, ht_mode:$ht_mode}"
wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" \
    -is channel "$channel" \
    -is ht_mode "$ht_mode" &&
        log "wm2/wm2_ht_mode_and_channel_iteration.sh: Settings applied to Wifi_Radio_State {channel:$channel, ht_mode:$ht_mode} - Success" ||
        raise "Failed to apply settings to Wifi_Radio_State {channel:$channel, ht_mode:$ht_mode}" -l "wm2/wm2_ht_mode_and_channel_iteration.sh" -tc

log "wm2/wm2_ht_mode_and_channel_iteration.sh: Waiting for channel to apply to Wifi_VIF_State {channel:$channel}"
wait_ovsdb_entry Wifi_VIF_State -w if_name "$vif_if_name" \
    -is channel "$channel" &&
        log "wm2/wm2_ht_mode_and_channel_iteration.sh: Settings applied to Wifi_VIF_State {channel:$channel} - Success" ||
        raise "Failed to apply settings to Wifi_VIF_State {channel:$channel}" -l "wm2/wm2_ht_mode_and_channel_iteration.sh" -tc

pass
