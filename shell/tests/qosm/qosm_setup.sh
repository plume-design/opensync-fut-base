#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
qosm/qosm_setup.sh [-h] arguments
Description:
    - Setup device for QOSM testing
Arguments:
    -h : show this help message
Script usage example:
    ./qosm/qosm_setup.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

device_init &&
    log -deb "qosm/qosm_setup.sh - Device initialized - Success" ||
    raise "device_init Could not initialize device" -l "qosm/qosm_setup.sh" -ds

empty_ovsdb_table AW_Debug  &&
    log -deb "qosm/qosm_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty table" -l "qosm/qosm_setup.sh" -ds

set_manager_log QOSM TRACE &&
    log -deb "qosm/qosm_setup.sh - Manager log for QOSM set to TRACE - Success" ||
    raise "set_manager_log QOSM TRACE - Could not set manager log severity" -l "qosm/qosm_setup.sh" -ds
