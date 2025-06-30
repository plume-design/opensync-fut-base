#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tools/device/remove_vif_interface.sh [-h] arguments
Description:
    - Removes Radio/VIF interface and validates it in State table
Arguments:
    -h  show this help message
    -if_name     : Wifi_Radio_Config::if_name : (string)(required)
    -vif_if_name : Wifi_VIF_Config::if_name   : (string)(required)
Script usage example:
    ./tools/device/remove_vif_interface.sh -if_name wifi0 -vif_if_name home-ap-24
usage_string
}

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/remove_vif_interface.sh" -arg

log "tools/device/$(basename "$0"): remove_vif_interface - Removing interface"
remove_vif_interface "$@" &&
    log "tools/device/$(basename "$0"): remove_vif_interface - Success" ||
    raise "remove_vif_interface - Failed" -l "tools/device/$(basename "$0")" -tc

exit 0
