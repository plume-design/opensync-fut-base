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
wm2/wm2_immutable_radio_freq_band.sh [-h] arguments
Description:
    - Script tries to set chosen FREQ BAND. This is IMMUTABLE field and it can't be changed. If interface is not UP it brings up
      the interface, and tries to set FREQ BAND to desired value. IF IMMUTABLE field is changed test will FAIL.
Arguments:
    -h  show this help message
    (radio_idx)        : Wifi_VIF_Config::vif_radio_idx               : (int)(required)
    (radio_if_name)    : Wifi_Radio_Config::if_name                   : (string)(required)
    (ssid)             : Wifi_VIF_Config::ssid                        : (string)(required)
    (channel)          : Wifi_Radio_Config::channel                   : (int)(required)
    (ht_mode)          : Wifi_Radio_Config::ht_mode                   : (string)(required)
    (hw_mode)          : Wifi_Radio_Config::hw_mode                   : (string)(required)
    (mode)             : Wifi_VIF_Config::mode                        : (string)(required)
    (vif_if_name)      : Wifi_VIF_Config::if_name                     : (string)(required)
    (freq_band)        : used as freq_band in Wifi_Radio_Config table : (string)(required)
    (channel_mode)     : Wifi_Radio_Config::channel_mode              : (string)(required)
    (enabled)          : Wifi_Radio_Config::enabled                   : (string)(required)
    (wpa)              : Wifi_VIF_Config::wpa                         : (string)(required)
    (wpa_key_mgmt)     : Wifi_VIF_Config::wpa_key_mgmt                : (string)(required)
    (wpa_psks)         : Wifi_VIF_Config::wpa_psks                    : (string)(required)
    (wpa_oftags)       : Wifi_VIF_Config::wpa_oftags                  : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_immutable_radio_freq_band.sh -vif_radio_idx <RADIO-IDX> -radio_if_name <IF-NAME> -ssid <SSID> -channel <CHANNEL> -ht_mode <HT-MODE> -hw_mode <HW-MODE> -mode <MODE> -vif_if_name <VIF-IF-NAME> -freq_band <FREQ-BAND> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
Script usage example:
    ./wm2/wm2_immutable_radio_freq_band.sh -vif_radio_idx 2 -radio_if_name wifi1 -ssid test_wifi_50L -channel 44 -ht_mode HT20 -hw_mode 11ac -mode ap -vif_if_name home-ap-l50 -freq_band 5GU -channel_mode manual -enabled "true"  -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=30
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_immutable_radio_freq_band.sh" -arg

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

# Parsing arguments passed to the script.
while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -hw_mode | \
        -mode | \
        -ssid | \
        -channel | \
        -vif_if_name | \
        -vif_radio_idx)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -radio_if_name)
            radio_if_name=${1}
            radio_vif_args="${radio_vif_args} -${option#?} ${radio_if_name}"
            shift
            ;;
        -channel_mode | \
        -enabled | \
        -ht_mode)
            create_radio_vif_args="${create_radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -freq_band)
            freq_band=${1}
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
            raise "Wrong option provided: $option" -l "wm2/wm2_immutable_radio_freq_band.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_immutable_radio_freq_band.sh: WM2 test - Immutable radio frequency band - '${freq_band}'"

log "wm2/wm2_immutable_radio_freq_band.sh: Checking if Radio/VIF states are valid for test"
check_radio_vif_state \
    ${radio_vif_args} &&
        log "wm2/wm2_immutable_radio_freq_band.sh: Radio/VIF states are valid" ||
            (
                log "wm2/wm2_immutable_radio_freq_band.sh: Cleaning VIF_Config"
                vif_reset
                log "wm2/wm2_immutable_radio_freq_band.sh: Radio/VIF states are not valid, creating interface..."
                create_radio_vif_interface \
                    ${radio_vif_args} \
                    ${create_radio_vif_args} &&
                        log "wm2/wm2_immutable_radio_freq_band.sh: create_radio_vif_interface - Interface $radio_if_name created - Success"
            ) ||
        raise "create_radio_vif_interface - Interface $radio_if_name not created" -l "wm2/wm2_immutable_radio_freq_band.sh" -ds

original_band=$(get_ovsdb_entry_value Wifi_Radio_State freq_band -w if_name "$radio_if_name")

if [ "$freq_band" = "$original_band" ]; then
    raise "Chosen FREQ BAND ($freq_band) needs to be DIFFERENT from default FREQ BAND ($original_band) - ['2.4G', '5G', '5GL', '5GU']" -l "wm2/wm2_immutable_radio_freq_band.sh" -arg
fi

log "wm2/wm2_immutable_radio_freq_band.sh: Changing FREQ BAND to $freq_band"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" -u freq_band "$freq_band" &&
    log "wm2/wm2_immutable_radio_freq_band.sh: update_ovsdb_entry - Wifi_Radio_Config::freq_band is $freq_band - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Radio_Config::freq_band is not $freq_band" -l "wm2/wm2_immutable_radio_freq_band.sh" -fc

res=$(wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is freq_band "$freq_band" -ec)

log "wm2/wm2_immutable_radio_freq_band.sh: Reversing FREQ BAND to normal value"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" -u freq_band "$original_band" &&
    log "wm2/wm2_immutable_radio_freq_band.sh: update_ovsdb_entry - Wifi_Radio_Config table::freq_band is $original_band - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Radio_Config::freq_band is not $original_band" -l "wm2/wm2_immutable_radio_freq_band.sh" -fc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is freq_band "$original_band" &&
    log "wm2/wm2_immutable_radio_freq_band.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::freq_band is $original_band - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::freq_band is not $original_band" -l "wm2/wm2_immutable_radio_freq_band.sh" -tc

if [ "$res" -eq 0 ]; then
    raise "Immutable field freq_band was changed to $freq_band" -l "wm2/wm2_immutable_radio_freq_band.sh" -tc
fi

pass
