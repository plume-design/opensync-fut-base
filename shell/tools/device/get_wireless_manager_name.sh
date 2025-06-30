#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tools/device/get_wireless_manager_name.sh [-h]
Description:
    - Script gets the name of the wireless manager from the device.
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/get_wireless_manager_name.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

get_wireless_manager_name ||
    raise "Failed to get wireless manager name from device" -l "tools/device/get_wireless_manager_name.sh" -s
