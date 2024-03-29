#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
ut/ut_setup.sh [-h] arguments
Description:
    - Setup device for UT testing
Arguments:
    -h : show this help message
Script usage example:
    ./ut/ut_setup.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

device_init &&
    log -deb "ut/ut_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "ut/ut_setup.sh" -ds

start_openswitch &&
    log -deb "ut/ut_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "ut/ut_setup.sh" -ds

restart_managers
log -deb "ut/ut_setup.sh: Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "ut/ut_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "ut/ut_setup.sh" -ds
