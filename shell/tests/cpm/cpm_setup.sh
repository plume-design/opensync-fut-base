#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

check_kconfig_option_exists "CONFIG_CPM_TINYPROXY_PATH" &&
  log -deb "cpm/cpm_setup.sh - The CONFIG_CPM_TINYPROXY_PATH kconfig option exists - Success" ||
  raise "The CONFIG_CPM_TINYPROXY_PATH kconfig option does not exist" -l "cpm/cpm_setup.sh" -ds

tinyproxy_path_value=$(get_kconfig_option_value "CONFIG_CPM_TINYPROXY_PATH")
# Clean string of quotes:
tinyproxy_path=$(echo ${tinyproxy_path_value} | tr -d '"')

[ -f "$tinyproxy_path" ] &&
  log -deb "cpm/cpm_setup.sh - The tinyproxy binary $tinyproxy_path exists - Success" ||
  raise "The tinyproxy binary $tinyproxy_path does not exist" -l "cpm/cpm_setup.sh" -ds

[ -x "$tinyproxy_path" ] &&
  log -deb "cpm/cpm_setup.sh - The tinyproxy binary $tinyproxy_path is executable - Success" ||
  raise "The tinyproxy binary $tinyproxy_path is not executable" -l "cpm/cpm_setup.sh" -ds

device_init &&
    log -deb "cpm/cpm_setup.sh - Device initialized - Success" ||
    raise "device_init - Could not initialize device" -l "cpm/cpm_setup.sh" -ds

empty_ovsdb_table AW_Debug &&
    log -deb "cpm/cpm_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "cpm/cpm_setup.sh" -ds

set_manager_log CPM TRACE &&
    log -deb "cpm/cpm_setup.sh - Manager log for CPM set to TRACE - Success" ||
    raise "set_manager_log CPM TRACE - Could not set manager log severity" -l "cpm/cpm_setup.sh" -ds

update_ovsdb_entry Node_Services -w service cpm \
    -u enable true ||
        raise "Could not update Node_Services" -l "unit_lib: service cpm enable true" -fc

wait_ovsdb_entry Node_Services -w service cpm \
    -is enable true \
    -is status enabled &&
        log "cpm/cpm_setup.sh - OpenSync captive portal manager is enabled on the device - Success" ||
        raise "Node_Services cpm status not enabled" -l "unit_lib: service cpm status not enabled" -fc
