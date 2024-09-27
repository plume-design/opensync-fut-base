#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

tc_name="tools/device/$(basename "$0")"
usage()
{
cat << usage_string
${tc_name} [-h] arguments
Description:
    - Script runs wm2_lib::create_vif_interface with given parameters
Arguments:
    -h  show this help message
See wm2_lib::create_vif_interface for more information
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables Wifi_VIF_Config Wifi_VIF_State Wifi_Radio_Config Wifi_Radio_State
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

create_vif_interface "$@" &&
    log "${tc_name}: create_vif_interface - Success" ||
    raise "create_vif_interface - Failed" -l "${tc_name}" -tc

exit 0
