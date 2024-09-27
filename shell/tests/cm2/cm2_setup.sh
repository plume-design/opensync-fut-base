#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
cm2/cm2_setup.sh [-h] arguments
Description:
    - Setup device for CM testing
Arguments:
    -h : show this help message
Script usage example:
    ./cm2/cm2_setup.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_CM" "y" ||
    raise "CONFIG_MANAGER_CM != y - CM not present on device" -l "cm2/cm2_setup.sh" -s

device_init &&
    log -deb "cm2/cm2_setup.sh - Device initialized - Success" ||
    raise "device_init - Could not initialize device" -l "cm2/cm2_setup.sh" -ds

empty_ovsdb_table AW_Debug &&
    log -deb "cm2/cm2_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty table:" -l "cm2/cm2_setup.sh" -ds

set_manager_log CM TRACE &&
    log -deb "cm2/cm2_setup.sh - Manager log for CM set to TRACE - Success" ||
    raise "set_manager_log CM TRACE - Could not set manager log severity" -l "cm2/cm2_setup.sh" -ds

wait_for_function_response 0 "check_default_route_gw" &&
    log -deb "cm2/cm2_setup.sh - Default GW added to routes - Success" ||
    raise "check_default_route_gw - Default GW not added to routes" -l "cm2/cm2_setup.sh" -ds
