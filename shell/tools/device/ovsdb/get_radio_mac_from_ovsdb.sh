#!/bin/sh

# FUT environment loading
# Script echoes single line so we are redirecting source output to /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source /tmp/fut-base/shell/config/default_shell.sh &> /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" &> /dev/null
[ -n "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -n "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

usage()
{
cat << usage_string
tools/device/ovsdb/get_radio_mac_from_ovsdb.sh [-h] arguments
Description:
    - This script gets radio physical (MAC) address from ovsdb
Arguments:
    -h  show this help message
    \$1 (where_clause) : ovsdb "where" clause for Wifi_Radio_State table, that determines how we get the MAC address : (string)(required)
Script usage example:
    ./tools/device/ovsdb/get_radio_mac_from_ovsdb.sh "if_name==wifi1"
    ./tools/device/ovsdb/get_radio_mac_from_ovsdb.sh "freq_band==5GL"
    ./tools/device/ovsdb/get_radio_mac_from_ovsdb.sh "channel==44"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    if [ $fut_ec -ne 0 ]; then
        fut_info_dump_line
        print_tables Wifi_Radio_State
        fut_info_dump_line
    fi
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/ovsdb/get_radio_mac_from_ovsdb.sh" -arg
where_clause="${1}"

# It is important that no logging is performed for functions that output values
fnc_str="get_radio_mac_from_ovsdb ${where_clause}"
wait_for_function_output "notempty" "${fnc_str}" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    iface_mac_raw=$($fnc_str) || raise "Failure: ${fnc_str}" -l "tools/device/ovsdb/get_radio_mac_from_ovsdb.sh" -fc
else
    raise "Failure: ${fnc_str}" -l "tools/device/ovsdb/get_radio_mac_from_ovsdb.sh" -fc
fi

echo -n "${iface_mac_raw}"
exit 0
