#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

check_kconfig_option "CONFIG_MANAGER_PM" "y" ||
    raise "CONFIG_MANAGER_PM != y - PM not present on device" -l "pm/pm_setup.sh" -s

device_init &&
    log -deb "pm/pm_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "pm/pm_setup.sh" -ds

start_openswitch &&
    log -deb "pm/pm_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "pm/pm_setup.sh" -ds

restart_managers
    log -deb "pm/pm_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "pm/pm_setup.sh - AW_Debug table emptied - Success"  ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty table" -l "pm/pm_setup.sh" -ds

set_manager_log PM TRACE &&
    log -deb "pm/pm_setup.sh - Manager log for PM set to TRACE - Success"||
    raise "FAIL: set_manager_log PM TRACE - Could not set manager log severity" -l "pm/pm_setup.sh" -ds
