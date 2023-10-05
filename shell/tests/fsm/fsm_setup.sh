#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

check_kconfig_option "CONFIG_MANAGER_FSM" "y" ||
    raise "CONFIG_MANAGER_FSM != y - FSM not present on device" -l "fsm/fsm_setup.sh" -s

device_init  &&
    log -deb "fsm/fsm_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "fsm/fsm_setup.sh" -ds

start_openswitch &&
    log -deb "fsm/fsm_setup.sh - OpenvSwitch started - Success"  ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "fsm/fsm_setup.sh" -ds

restart_managers
log -deb "fsm/fsm_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "fsm/fsm_setup.sh - AW_Debug table emptied - Success"  ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty table" -l "fsm/fsm_setup.sh" -ds

set_manager_log FSM TRACE &&
    log -deb "fsm/fsm_setup.sh - Manager log for FSM set to TRACE - Success"||
    raise "FAIL: set_manager_log FSM TRACE - Could not set manager log severity" -l "fsm/fsm_setup.sh" -ds
