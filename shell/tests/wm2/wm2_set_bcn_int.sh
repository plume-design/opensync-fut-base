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
    - Script tries to set chosen BEACON INTERVAL. If interface is not UP it brings up the interface, and tries to set
      BEACON INTERVAL to desired value.
Arguments:
    -h  show this help message
    (if_name)       : Wifi_Radio_Config::if_name     : (string)(required)
    (vif_if_name)   : Wifi_VIF_Config::if_name       : (string)(required)
    (vif_radio_idx) : Wifi_VIF_Config::vif_radio_idx : (int)(required)
    (ssid)          : Wifi_VIF_Config::ssid          : (string)(required)
    (channel)       : Wifi_Radio_Config::channel     : (int)(required)
    (ht_mode)       : Wifi_Radio_Config::ht_mode     : (string)(required)
    (hw_mode)       : Wifi_Radio_Config::hw_mode     : (string)(required)
    (mode)          : Wifi_VIF_Config::mode          : (string)(required)
    (bcn_int)       : Wifi_Radio_Config::bcn_int     : (int)(required)
    (channel_mode)  : Wifi_Radio_Config::channel_mode: (string)(required)
    (enabled)       : Wifi_Radio_Config::enabled     : (string)(required)
    (wifi_security_type) : 'wpa' if wpa fields are used or 'legacy' if security fields are used: (string)(required)

Wifi Security arguments(choose one or the other):
    If 'wifi_security_type' == 'wpa' (preferred)
    (wpa)           : Wifi_VIF_Config::wpa           : (string)(required)
    (wpa_key_mgmt)  : Wifi_VIF_Config::wpa_key_mgmt  : (string)(required)
    (wpa_psks)      : Wifi_VIF_Config::wpa_psks      : (string)(required)
    (wpa_oftags)    : Wifi_VIF_Config::wpa_oftags    : (string)(required)
                    (OR)
    If 'wifi_security_type' == 'legacy' (deprecated)
    (security)      : Wifi_VIF_Config::security      : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_bcn_int.sh -if_name <IF-NAME> -vif_if_name <VIF-IF-NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT-MODE> -hw_mode <HW-MODE> -mode <MODE> -bcn_int <BCN_INT> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
                    (OR)
                 Run: ./wm2/wm2_set_bcn_int.sh -if_name <IF-NAME> -vif_if_name <VIF-IF-NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT-MODE> -hw_mode <HW-MODE> -mode <MODE> -bcn_int <BCN_INT> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -security <SECURITY>

Script usage example:
    ./wm2/wm2_set_bcn_int.sh -if_name wifi1 -vif_if_name home-ap-l50 -vif_radio_idx 2 -ssid FUTssid -channel 36 -ht_mode HT20 -hw_mode 11ac -mode ap -bcn_int 200 -channel_mode manual -enabled "true" -wifi_security_type wpa -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
    ./wm2/wm2_set_bcn_int.sh -if_name wifi1 -vif_if_name home-ap-l50 -vif_radio_idx 2 -ssid FUTssid -channel 36 -ht_mode HT20 -hw_mode 11ac -mode ap -bcn_int 200 -channel_mode manual -enabled "true" -wifi_security_type legacy -security '["map",[["encryption","WPA-PSK"],["key","FutTestPSK"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=26
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_set_bcn_int.sh" -arg

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
        -mode | \
        -ssid | \
        -channel | \
        -hw_mode | \
        -vif_radio_idx)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -if_name)
            if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${if_name}"
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
        -bcn_int)
            bcn_int=${1}
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
            [ "${wifi_security_type}" != "wpa" ] && raise "FAIL: Incorrect combination of WPA and legacy wifi security type provided" -l "wm2/wm2_set_bcn_int.sh" -arg
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -security)
            [ "${wifi_security_type}" != "legacy" ] && raise "FAIL: Incorrect combination of WPA and legacy wifi security type provided" -l "wm2/wm2_set_bcn_int.sh" -arg
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        *)
            raise "FAIL: Wrong option provided: $option" -l "wm2/wm2_set_bcn_int.sh" -arg
            ;;
    esac
done
log_title "wm2/wm2_set_bcn_int.sh: WM2 test - Testing Wifi_Radio_Config field bcn_int - '${bcn_int}'}"

log "wm2/wm2_set_bcn_int.sh: Checking if Radio/VIF states are valid for test"
check_radio_vif_state \
    ${radio_vif_args} &&
        log "wm2/wm2_set_bcn_int.sh: Radio/VIF states are valid" ||
            (
                log "wm2/wm2_set_bcn_int.sh: Cleaning VIF_Config"
                vif_reset
                log "wm2/wm2_set_bcn_int.sh: Radio/VIF states are not valid, creating interface..."
                create_radio_vif_interface \
                    ${radio_vif_args} \
                    ${create_radio_vif_args} \
                    -disable_cac &&
                        log "wm2/wm2_set_bcn_int.sh: create_radio_vif_interface - Interface $if_name created - Success"
            ) ||
        raise "FAIL: create_radio_vif_interface - Interface $if_name not created" -l "wm2/wm2_set_bcn_int.sh" -ds

log "wm2/wm2_set_bcn_int.sh: Changing bcn_int to $bcn_int"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$if_name" -u bcn_int "$bcn_int" &&
    log "wm2/wm2_set_bcn_int.sh: update_ovsdb_entry - Wifi_Radio_Config::bcn_int is $bcn_int - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Radio_Config::bcn_int is not $bcn_int" -l "wm2/wm2_set_bcn_int.sh" -oe

wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is bcn_int "$bcn_int" &&
    log "wm2/wm2_set_bcn_int.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::bcn_int is $bcn_int - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::bcn_int is not $bcn_int" -l "wm2/wm2_set_bcn_int.sh" -tc

if [ $FUT_SKIP_L2 != 'true' ]; then
log "wm2/wm2_set_bcn_int.sh: Checking BEACON INTERVAL set on system - LEVEL2"
    check_beacon_interval_at_os_level "$bcn_int" "$vif_if_name" ||
        log "wm2/wm2_set_bcn_int.sh: LEVEL2 - check_beacon_interval_at_os_level - BEACON INTERVAL $bcn_int set on system - Success" ||
        raise "FAIL: LEVEL2 - check_beacon_interval_at_os_level - BEACON INTERVAL $bcn_int not set on system" -l "wm2/wm2_set_bcn_int.sh" -tc
fi

pass
