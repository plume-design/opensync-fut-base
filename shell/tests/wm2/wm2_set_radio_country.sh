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
wm2/wm2_set_radio_country.sh [-h] arguments
Description:
    - Script checks if 'country' in Wifi_Radio_State at given radio interface is set to the regulatory domain of the device.
Arguments:
    -h  show this help message
    \$1  (if_name)          : Wifi_Radio_Config::if_name          : (string)(required)
    \$2  (country_to_check) : Wifi_Radio_Config::country to check : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_set_radio_country.sh <IF-NAME> <COUNTRY>
Script usage example:
    ./wm2/wm2_set_radio_country.sh wifi1 US
    ./wm2/wm2_set_radio_country.sh wl1 E0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wm2/wm2_set_radio_country.sh" -arg
if_name=$1
country_to_check=$2

trap '
    fut_info_dump_line
    print_tables Wifi_Radio_State
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "wm2/wm2_set_radio_country.sh: WM2 test - Testing Wifi_Radio_State field country - '${country_to_check}'"

check_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -w country "$country_to_check" &&
    log "wm2/wm2_set_radio_country.sh: wait_ovsdb_entry - Wifi_Radio_State::country is $country_to_check - Success" ||
    raise "FAIL: wait_ovsdb_entry - Wifi_Radio_State::country is not $country_to_check" -l "wm2/wm2_set_radio_country.sh" -tc

pass
