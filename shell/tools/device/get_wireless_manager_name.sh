#!/bin/sh

# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

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

get_wireless_manager_name
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
    exit 0
else
    raise "Failed to get wireless manager name from device" -l "tools/device/get_wireless_manager_name.sh" -s
fi
