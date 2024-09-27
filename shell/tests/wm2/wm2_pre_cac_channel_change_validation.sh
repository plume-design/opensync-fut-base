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
wm2/wm2_pre_cac_channel_change_validation.sh [-h] arguments
Testcase info:

Arguments:
    -h  show this help message
    (radio_if_name)      : Wifi_Radio_Config::if_name        : (string)(required)
    (vif_if_name)        : Wifi_VIF_Config::if_name          : (string)(required)
    (vif_radio_idx)      : Wifi_VIF_Config::vif_radio_idx    : (int)(required)
    (ssid)               : Wifi_VIF_Config::ssid             : (string)(required)
    (channel_a)          : Wifi_Radio_Config::channel        : (int)(required)
    (channel_b)          : Wifi_Radio_Config::channel        : (int)(required)
    (ht_mode)            : Wifi_Radio_Config::ht_mode        : (string)(required)
    (hw_mode)            : Wifi_Radio_Config::hw_mode        : (string)(required)
    (mode)               : Wifi_VIF_Config::mode             : (string)(required)
    (channel_mode)       : Wifi_Radio_Config::channel_mode   : (string)(required)
    (enabled)            : Wifi_Radio_Config::enabled        : (string)(required)
    (reg_domain)         : Interface regulatory domain       : (string)(required)
    (wpa)                : Wifi_VIF_Config::wpa              : (string)(required)
    (wpa_key_mgmt)       : Wifi_VIF_Config::wpa_key_mgmt     : (string)(required)
    (wpa_psks)           : Wifi_VIF_Config::wpa_psks         : (string)(required)
    (wpa_oftags)         : Wifi_VIF_Config::wpa_oftags       : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_pre_cac_channel_change_validation.sh -radio_if_name <IF_NAME> -vif_if_name <VIF_IF_NAME> -vif_radio_idx <VIF-RADIO-IDX> -ssid <SSID> -channel_a <CHANNEL_A> -channel_b <CHANNEL_B> -ht_mode <HT_MODE> -hw_mode <HW_MODE> -mode <MODE> -channel_mode <CHANNEL_MODE> -enabled <ENABLED> -wifi_security_type <WIFI_SECURITY_TYPE> -wpa <WPA> -wpa_key_mgmt <WPA_KEY_MGMT> -wpa_psks <WPA_PSKS> -wpa_oftags <WPA_OFTAGS>
Script usage example:
    ./wm2/wm2_pre_cac_channel_change_validation.sh -radio_if_name wifi2 -vif_if_name home-ap-u50 -vif_radio_idx 2 -ssid FUTssid -channel_a 120 -channel_b 104 -ht_mode HT20 -hw_mode 11ac -mode ap  -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=32
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -arg

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
        -ht_mode | \
        -mode | \
        -vif_if_name | \
        -vif_radio_idx | \
        -hw_mode | \
        -ssid | \
        -channel_mode | \
        -enabled)
            radio_vif_args_a="${radio_vif_args_a} -${option#?} ${1}"
            shift
            ;;
        -radio_if_name)
            radio_if_name=${1}
            radio_vif_args_a="${radio_vif_args_a} -${option#?} ${radio_if_name}"
            shift
            ;;
        -channel_a)
            channel_a=${1}
            radio_vif_args_a="${radio_vif_args_a} -channel ${channel_a}"
            shift
            ;;
        -channel_b)
            channel_b=${1}
            shift
            ;;
        -reg_domain)
            reg_domain=${1}
            shift
            ;;
        -wpa | \
        -wpa_key_mgmt | \
        -wpa_psks | \
        -wpa_oftags)
            radio_vif_args_a="${radio_vif_args_a} -${option#?} ${1}"
            shift
            ;;
        *)
            raise "Wrong option provided: $option" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_pre_cac_channel_change_validation.sh: WM2 test - PRE-CAC - Using: '${channel_a}'->'${channel_b}'"

# Testcase:
# Configure radio, create VIF and apply channel
log "wm2/wm2_pre_cac_channel_change_validation.sh: Configuring Wifi_Radio_Config, creating interface in Wifi_VIF_Config."
log "wm2/wm2_pre_cac_channel_change_validation.sh: Waiting for ${channel_change_timeout}s for settings {channel:$channel_a}"
create_radio_vif_interface \
    ${radio_vif_args_a} \
    -timeout ${channel_change_timeout} &&
        log "wm2/wm2_pre_cac_channel_change_validation.sh: create_radio_vif_interface {$radio_if_name, $channel_a} - Success" ||
        raise "create_radio_vif_interface {$radio_if_name, $channel_a} - Interface not created" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

# Validate CAC elapsed for channel
validate_cac "${radio_if_name}" &&
    log -deb "wm2/wm2_pre_cac_channel_change_validation.sh: - CAC validated for channel ${channel_b}" ||
    raise "validate_cac - Failed to validate CAC for $channel_b" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

# Validate PRE-CAC behaviour for channel
validate_pre_cac_behaviour ${radio_if_name} ${reg_domain} &&
    echo "wm2/wm2_pre_cac_channel_change_validation.sh: PRE-CAC validated." ||
    raise "PRE-CAC is not correct" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

# Update channel to channel_b, validate CAC for range
log "wm2/wm2_pre_cac_channel_change_validation.sh: Changing channel to $channel_b"
update_ovsdb_entry Wifi_Radio_Config -w if_name "$radio_if_name" -u channel "$channel_b" &&
    log "wm2/wm2_pre_cac_channel_change_validation.sh: update_ovsdb_entry - Wifi_Radio_Config::channel is $channel_b - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Radio_Config::channel is not $channel_b" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

wait_ovsdb_entry Wifi_Radio_State -w if_name "$radio_if_name" -is channel "$channel_b" &&
    log "wm2/wm2_pre_cac_channel_change_validation.sh: wait_ovsdb_entry - Wifi_Radio_Config reflected to Wifi_Radio_State::channel is $channel_b - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Radio_Config to Wifi_Radio_State::channel is not $channel_b" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

# Validate CAC elapsed for channel
validate_cac "${radio_if_name}" &&
    log -deb "wm2/wm2_pre_cac_channel_change_validation.sh: - CAC validated for channel ${channel_b}" ||
    raise "validate_cac - Failed to validate CAC for $channel_b" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

# Validate PRE-CAC behaviour for channel
validate_pre_cac_behaviour ${radio_if_name} ${reg_domain} &&
    echo "wm2/wm2_pre_cac_channel_change_validation.sh: PRE-CAC validated." ||
    raise "PRE-CAC is not correct" -l "wm2/wm2_pre_cac_channel_change_validation.sh" -tc

pass
