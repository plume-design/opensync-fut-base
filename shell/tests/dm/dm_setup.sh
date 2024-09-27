#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
dm/dm_setup.sh [-h] arguments
Description:
    - Setup device for DM testing
Arguments:
    -h : show this help message
    \$@ (radio_if_names) : wait for if_name in Wifi_Radio_State table to be present after setup : (string)(optional)
Script usage example:
    ./dm/dm_setup.sh
    ./dm/dm_setup.sh wifi0 wifi1
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

device_init &&
    log -deb "dm/dm_setup.sh - Device initialized - Success" ||
    raise "device_init - Could not initialize device" -l "dm/dm_setup.sh" -ds

empty_ovsdb_table AW_Debug &&
    log -deb "dm/dm_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "dm/dm_setup.sh" -ds

set_manager_log DM TRACE &&
    log -deb "dm/dm_setup.sh - Manager log for DM set to TRACE - Success" ||
    raise "set_manager_log DM TRACE - Could not set manager log severity" -l "dm/dm_setup.sh" -ds

# Check if all radio interfaces are created
for if_name in "$@"
do
    wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is if_name "$if_name" &&
        log -deb "dm/dm_setup.sh - Wifi_Radio_State::if_name '$if_name' present - Success" ||
        raise "Wifi_Radio_State::if_name for '$if_name' does not exist" -l "dm/dm_setup.sh" -ds
done
