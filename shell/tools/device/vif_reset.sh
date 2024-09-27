#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tools/device/vif_reset.sh [-h] arguments
Description:
    - Script is used to reset STA VIF interfaces and remove AP VIF interfaces from Wifi_VIF_Config
      table and waits for the State table to reflect.
    - Specific interface names, which should be reset, can be passed to this script as optional
      arguments.
Arguments:
    -h  show this help message
    - [interface1] [interface2] ... : One or multiple interfaces which should be reset : (str)(optional)
Script usage example:
    ./tools/device/vif_reset.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables Wifi_VIF_Config Wifi_VIF_State
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

vif_reset "$@" ||
    raise "vif_reset - Failed" -l "tools/device/vif_reset.sh" -tc

exit 0
