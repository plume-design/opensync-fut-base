#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

device_init &&
    log -deb "nfm/nfm_setup.sh - Device initialized - Success" ||
    raise "device_init - Could not initialize device" -l "nfm/nfm_setup.sh" -ds

empty_ovsdb_table AW_Debug &&
    log -deb "nfm/nfm_setup.sh - AW_Debug table emptied - Success"  ||
    raise "Could not empty table: empty_ovsdb_table AW_Debug" -l "nfm/nfm_setup.sh" -ds

set_manager_log NFM TRACE &&
    log -deb "nfm/nfm_setup.sh - Manager log for NFM set to TRACE - Success"||
    raise "Could not set manager log severity: set_manager_log NFM TRACE" -l "nfm/nfm_setup.sh" -ds
