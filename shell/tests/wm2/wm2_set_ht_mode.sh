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
default_channel_change_timeout=60

usage()
{
cat << usage_string
wm2/wm2_set_ht_mode.sh [-h] arguments
Description:
    - Script tries to set chosen HT MODE. This script expects a VIF to already be configured on the device.
Arguments:
    -h  show this help message
    (radio_if_name) : Wifi_Radio_Config::if_name     : (string)(required)
    (vif_if_name)   : Wifi_VIF_Config::if_name       : (string)(required)
    (channel)       : Wifi_Radio_Config::channel     : (int)(required)
    (ht_mode)       : Wifi_Radio_Config::ht_mode     : (string)(required)

Script usage example:
    ./wm2/wm2_set_ht_mode.sh -if_name wifi1 -vif_if_name home-ap-l50 -channel 36 -ht_mode HT20
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=4
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_ht_mode.sh" -arg

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
    esac
done

log_title "wm2/wm2_set_ht_mode.sh: WM2 test - Testing Wifi_Radio_Config field ht_mode - '${ht_mode}'"

update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" \
    -u ht_mode "$ht_mode" &&
        log -deb "wm2/wm2_set_ht_mode.sh: update_ovsdb_entry - Wifi_Radio_Config ht_mode was updated to $ht_mode - Success" ||
        raise "Failed to update Wifi_Radio_Config with $ht_mode" -l "unit_lib:configure_sta_interface" -l "wm2/wm2_set_ht_mode.sh" -tc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is ht_mode "$ht_mode" &&
    log "wm2/wm2_set_ht_mode.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::ht_mode is $ht_mode - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::ht_mode is not $ht_mode" -l "wm2/wm2_set_ht_mode.sh" -tc

log "wm2/wm2_set_ht_mode.sh: Checking ht_mode at system level - LEVEL2"
check_ht_mode_at_os_level "$ht_mode" "$vif_if_name" "$channel" &&
    log "wm2/wm2_set_ht_mode.sh: LEVEL2 - check_ht_mode_at_os_level - ht_mode $ht_mode set at system level - Success" ||
    raise "LEVEL2 - check_ht_mode_at_os_level - ht_mode  $ht_mode not set at system level" -l "wm2/wm2_set_ht_mode.sh" -tc

pass
