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
wm2/wm2_transmit_rate_boost.sh [-h] arguments
Description:
    - Script disables the 1 Mbps and 2 Mbps data rates for beacons, probe responses and multicast/broadcast frames in
      order to reduce airtime consumption.
Arguments:
    -h  show this help message
    (radio_if_name) : Wifi_Radio_Config::if_name : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_transmit_rate_boost.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "wm2/wm2_transmit_rate_boost.sh" -arg
radio_if_name=${1}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

BASIC_RATES='["set",["11","5.5"]]'
BEACON_RATE='["set",["5.5"]]'
MCAST_RATE='["set",["5.5"]]'
MGMT_RATE='["set",["5.5"]]'
SUPPORTED_RATES='["set",["11","12","18","24","36","48","5.5","54","6","9"]]'

# Update Wifi_Radio_Config OVSDB table with new transmit rate arguments
update_ovsdb_entry Wifi_Radio_Config \
    -w if_name "$radio_if_name" \
    -u basic_rates $BASIC_RATES \
    -u beacon_rate $BEACON_RATE \
    -u mcast_rate $MCAST_RATE \
    -u mgmt_rate $MGMT_RATE \
    -u supported_rates $SUPPORTED_RATES &&
        log "wm2/wm2_transmit_rate_boost.sh: update_ovsdb_entry - Updated transmit rate parameters - Success" ||
        raise "update_ovsdb_entry - Failed to update transmit rate parameters" -l "wm2/wm2_transmit_rate_boost.sh" -fc
