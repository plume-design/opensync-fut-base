#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm


tc_name="device/ovsdb/$(basename "$0")"
usage()
{
cat << usage_string
${tc_name} [-h] arguments
Description:
    - Script runs unit_lib::check_ovsdb_table_field_exists with given parameters
Arguments:
    -h  show this help message
    See unit_lib::check_ovsdb_table_field_exists for more information
Script usage example:
    ./${tc_name} Wifi_VIF_Config wpa
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_ovsdb_table_field_exists "$@" && exit 0 || exit 1
