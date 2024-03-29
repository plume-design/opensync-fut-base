#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
qm/qm_setup.sh [-h] arguments
Description:
    - Setup device for QM testing
Arguments:
    -h : show this help message
Script usage example:
    ./qm/qm_setup.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_QM" "y" ||
    raise "CONFIG_MANAGER_QM != y - QM is not present on the device" -l "qm/qm_setup.sh" -s

device_init &&
    log -deb "qm/qm_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "qm/qm_setup.sh" -ds

start_openswitch &&
    log -deb "qm/qm_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "qm/qm_setup.sh" -ds

restart_managers
    log -deb "qm/qm_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "qm/qm_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "qm/qm_setup.sh" -ds
