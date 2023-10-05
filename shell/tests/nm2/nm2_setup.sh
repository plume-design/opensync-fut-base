#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

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
    raise "FAIL: device_init Could not initialize device" -l "nm2/nm2_setup.sh" -ds

start_openswitch &&
    log -deb "nm2/nm2_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "nm2/nm2_setup.sh" -ds

start_wireless_driver &&
    log -deb "nm2/nm2_setup.sh - Wireless driver started - Success" ||
    raise "FAIL: start_wireless_driver - Could not start wireless driver" -l "nm2/nm2_setup.sh" -ds

restart_managers
log -deb "nm2/nm2_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug  &&
    log -deb "nm2/nm2_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty table" -l "nm2/nm2_setup.sh" -ds

set_manager_log WM TRACE &&
    log -deb "nm2/nm2_setup.sh - Manager log for WM set to TRACE - Success" ||
    raise "FAIL: set_manager_log WM TRACE - Could not set manager log severity" -l "nm2/nm2_setup.sh" -ds

set_manager_log NM TRACE &&
    log -deb "nm2/nm2_setup.sh - Manager log for NM set to TRACE - Success" ||
    raise "FAIL: set_manager_log NM TRACE - Could not set manager log severity" -l "nm2/nm2_setup.sh" -ds

# Check if radio interfaces are created
for if_name in "$@"
do
    wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is if_name "$if_name" &&
        log -deb "nm2/nm2_setup.sh - Wifi_Radio_State::if_name '$if_name' present - Success" ||
        raise "FAIL: Wifi_Radio_State::if_name for '$if_name' does not exist" -l "nm2/nm2_setup.sh" -ds
done
