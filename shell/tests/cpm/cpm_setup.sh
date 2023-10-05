#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

check_kconfig_option "CONFIG_CPM_TINYPROXY_PATH" "\"/usr/sbin/tinyproxy\"" ||
    raise "CONFIG_CPM_TINYPROXY_PATH != /usr/sbin/tinyproxy - CPM tinyproxy path error" -l "cpm/cpm_setup.sh" -s

device_init &&
    log -deb "cpm/cpm_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "cpm/cpm_setup.sh" -ds

start_openswitch &&
    log -deb "cpm/cpm_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "cpm/cpm_setup.sh" -ds

restart_managers
log -deb "cpm/cpm_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "cpm/cpm_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "cpm/cpm_setup.sh" -ds

set_manager_log CPM TRACE &&
    log -deb "cpm/cpm_setup.sh - Manager log for CPM set to TRACE - Success" ||
    raise "FAIL: set_manager_log CPM TRACE - Could not set manager log severity" -l "cpm/cpm_setup.sh" -ds

update_ovsdb_entry Node_Services -w service cpm \
    -u enable true ||
        raise "FAIL: Could not update Node_Services" -l "unit_lib: service cpm enable true" -oe

wait_ovsdb_entry Node_Services -w service cpm \
    -is enable true \
    -is status enabled &&
        log "cpm/cpm_setup.sh - OpenSync captive portal manager is enabled on the device - Success" ||
        raise "FAIL: Node_Services cpm status not enabled" -l "unit_lib: service cpm status not enabled" -ow
