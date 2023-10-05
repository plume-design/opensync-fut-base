#!/bin/sh

# FUT environment loading
# Script echoes single line so we are redirecting source output to /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source /tmp/fut-base/shell/config/default_shell.sh &> /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" &> /dev/null
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -n "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null


tc_name="device/ovsdb/$(basename "$0")"
usage()
{
cat << usage_string
${tc_name} [-h] arguments
Description:
    - Script runs unit_lib::wait_ovsdb_entry with given parameters
Arguments:
    -h  show this help message
    See unit_lib::wait_ovsdb_entry for more information
Script usage example:
    ./${tc_name} Wifi_VIF_Config -w if_name home-ap-24
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

wait_ovsdb_entry "$@" && exit 0 || exit 1
