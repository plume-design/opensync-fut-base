#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
nm2/nm2_setup.sh [-h] arguments
Description:
    - Setup device for NM testing
Arguments:
    -h : show this help message
    \$@ (radio_if_names) : wait for if_name in Wifi_Radio_State table to be present after setup : (string)(optional)
Script usage example:
    ./nm2/nm2_setup.sh
    ./nm2/nm2_setup.sh wifi0 wifi1
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

device_init &&
    log -deb "nm2/nm2_setup.sh - Device initialized - Success" ||
    raise "device_init Could not initialize device" -l "nm2/nm2_setup.sh" -ds

empty_ovsdb_table AW_Debug  &&
    log -deb "nm2/nm2_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty table" -l "nm2/nm2_setup.sh" -ds

set_manager_log WM TRACE &&
    log -deb "nm2/nm2_setup.sh - Manager log for WM set to TRACE - Success" ||
    raise "set_manager_log WM TRACE - Could not set manager log severity" -l "nm2/nm2_setup.sh" -ds

set_manager_log NM TRACE &&
    log -deb "nm2/nm2_setup.sh - Manager log for NM set to TRACE - Success" ||
    raise "set_manager_log NM TRACE - Could not set manager log severity" -l "nm2/nm2_setup.sh" -ds
