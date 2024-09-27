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
wm2/wm2_check_wifi_credential_config.sh [-h] arguments
Description:
    - Script checks Wifi_Credential_Config table empty or not.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_check_wifi_credential_config.sh
Script usage example:
    ./wm2/wm2_check_wifi_credential_config.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_info_dump_line
    print_tables Wifi_Credential_Config
    fut_info_dump_line
' EXIT INT TERM

log_title "wm2/wm2_check_wifi_credential_config.sh: WM2 test - checks Wifi_Credential_Config table is empty or not"

if [ "$(${OVSH} s Wifi_Credential_Config -r | wc -l)" -gt 0 ]; then
    log "wm2/wm2_check_wifi_credential_config.sh: Pre-populated entry present in Wifi_Credential_Config table - Success"
else
    raise "Wifi_Credential_Config table is empty" -l "wm2/wm2_check_wifi_credential_config.sh" -tc
fi

pass
