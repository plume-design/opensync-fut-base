#!/bin/sh

# FUT environment loading
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source /tmp/fut-base/shell/config/default_shell.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}"
[ -n "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}"


tc_name="device/ovsdb/$(basename "$0")"
usage()
{
cat << usage_string
${tc_name} [-h] arguments
Description:
    - Script runs unit_lib::update_ovsdb_entry with given parameters
Arguments:
    -h  show this help message
    See unit_lib::update_ovsdb_entry for more information
Script usage example:
    ./${tc_name} Wifi_VIF_Config -w if_name home-ap-24 -u ssid "new_ssid"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

update_ovsdb_entry "$@" && exit 0 || exit 1
