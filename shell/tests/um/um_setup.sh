#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
um/um_setup.sh [-h] arguments
Description:
    - Setup device for UM testing
Arguments:
    -h : show this help message
    \$1 (fw_path) : Path where UM downloads FW files : (string) (required)
Script usage example:
    ./um/um_setup.sh /tmp/pfirmware
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] &&
    raise "um/um_setup.sh requires ${NARGS} input argument(s), $# given" -arg

fw_path=$1

check_kconfig_option "CONFIG_MANAGER_UM" "y" ||
    raise "CONFIG_MANAGER_UM != y - UM not present on device" -l "um/um_setup.sh" -s

device_init &&
    log -deb "um/um_setup.sh - Device initialized - Success" ||
    raise "device_init - Could not initialize device" -l "um/um_setup.sh" -ds

log -deb "um/um_setup.sh - Erasing $fw_path"
rm -rf "$fw_path" ||
    true

empty_ovsdb_table AW_Debug &&
    log -deb "um/um_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "um/um_setup.sh" -ds

set_manager_log UM TRACE &&
    log -deb "um/um_setup.sh - Manager log for UM set to TRACE - Success" ||
    raise "set_manager_log UM TRACE - Could not set manager log severity" -l "um/um_setup.sh" -ds
