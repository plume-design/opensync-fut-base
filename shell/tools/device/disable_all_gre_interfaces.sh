#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tools/device/disable_all_gre_interfaces.sh [-h] arguments
Description:
    - This script disables all GRE interfaces by setting their enabled state to false
    in the Wifi_Inet_Config table.
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/disable_all_gre_interfaces.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "tools/device/disable_all_gre_interfaces.sh: Disabling all GRE interfaces"

disable_all_gre_interfaces &&
    log -deb "tools/device/disable_all_gre_interfaces.sh: Success: disable_all_gre_interfaces" ||
    raise "Failed: disable_all_gre_interfaces" -l "tools/device/disable_all_gre_interfaces.sh" -ds

exit 0
