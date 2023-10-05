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
    \$1 (fw_download_path) : Path where UM downloads FW files : (string) (required)
    \$2 (if_name)          : Interface name for udhcpc start  : (string) (optional) : (default:eth0)
Script usage example:
    ./um/um_setup.sh /tmp/pfirmware eth0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS_MIN=1
NARGS_MAX=2
[ $# -ge ${NARGS_MIN} ] && [ $# -le ${NARGS_MAX} ] ||
    (usage && raise "Requires at least ${NARGS} input argument(s)" -l "um/um_setup.sh" -arg)

check_kconfig_option "CONFIG_MANAGER_UM" "y" ||
    raise "CONFIG_MANAGER_UM != y - UM not present on device" -l "um/um_setup.sh" -s

fw_path=$1
if_name=${2:-eth0}

device_init &&
    log -deb "um/um_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "um/um_setup.sh" -ds

start_openswitch &&
    log -deb "um/um_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "um/um_setup.sh" -ds

start_udhcpc "$if_name" true &&
    log -deb "um/um_setup.sh - start_udhcpc on '$if_name' started - Success" ||
    raise "FAIL: start_udhcpc - Could not start DHCP client" -l "um/um_setup.sh" -ds

log -deb "um/um_setup.sh - Erasing $fw_path"
rm -rf "$fw_path" ||
    true

restart_managers
log -deb "um/um_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "um/um_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "um/um_setup.sh" -ds

set_manager_log UM TRACE &&
    log -deb "um/um_setup.sh - Manager log for UM set to TRACE - Success" ||
    raise "FAIL: set_manager_log UM TRACE - Could not set manager log severity" -l "um/um_setup.sh" -ds
