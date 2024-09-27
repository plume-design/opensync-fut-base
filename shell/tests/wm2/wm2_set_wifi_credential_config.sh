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
wm2/wm2_set_wifi_credential_config.sh [-h] arguments
Description:
    - Script sets fields ssid, security and onboard_type of valid values into
      Wifi_Credential_Config and verify the applied field values.
Arguments:
    -h  show this help message
    \$1  (ssid)          : Wifi_Credential_Config::ssid          : (string)(required)
    \$2  (security)      : Wifi_Credential_Config::security      : (string)(required)
    \$3  (onboard_type)  : Wifi_Credential_Config::onboard_type  : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_wifi_credential_config.sh <SSID> <SECURITY> <ONBOARD_TYPE>
Script usage example:
    ./wm2/wm2_set_wifi_credential_config.sh FUTssid '["map",[["encryption","WPA-PSK"],["key","FUTpsk"]]]' gre
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wm2/wm2_set_wifi_credential_config.sh" -arg
ssid=${1}
security=${2}
onboard_type=${3}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Credential_Config
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "wm2/wm2_set_wifi_credential_config.sh: WM2 test - Set valid field values to Wifi_Credential_Config and verify fields are applied"

check_kconfig_option "CONFIG_MANAGER_WM" "y" ||
    raise "CONFIG_MANAGER_WM != y - WM is not present on the device" -l "wm2/wm2_set_wifi_credential_config.sh" -tc

log "wm2/wm2_set_wifi_credential_config.sh: Inserting ssid, security and onboard_type values into Wifi_Credential_Config"
${OVSH} i Wifi_Credential_Config ssid:="$ssid" security:="$security" onboard_type:="$onboard_type" &&
    log "wm2/wm2_set_wifi_credential_config.sh: insert_ovsdb_entry - Values inserted into Wifi_Credential_Config table - Success" ||
    raise "insert_ovsdb_entry - Failed to insert values into Wifi_Credential_Config" -l "wm2/wm2_set_wifi_credential_config.sh" -fc

wait_ovsdb_entry Wifi_Credential_Config -w ssid $ssid -is security $security -is onboard_type $onboard_type &&
    log "wm2/wm2_set_wifi_credential_config.sh: Values applied into Wifi_Credential_Config - Success" ||
    raise "Could not apply values into Wifi_Credential_Config" -l "wm2/wm2_set_wifi_credential_config.sh" -tc

pass
