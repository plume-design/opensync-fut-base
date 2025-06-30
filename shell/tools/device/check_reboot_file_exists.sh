#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

dm_setup_file="dm/dm_setup.sh"

usage()
{
cat << usage_string
tools/device/check_reboot_file_exists.sh [-h]
Description:
    - Script checks if reboot file exists.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${dm_setup_file} (see ${dm_setup_file} -h)
    - On DEVICE: Run: ./tools/device/check_reboot_file_exists.sh
Script usage example:
    ./tools/device/check_reboot_file_exists.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables Reboot_Status
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

check_kconfig_option "CONFIG_OSP_REBOOT_PSTORE" "y" ||
    raise "CONFIG_OSP_REBOOT_PSTORE != y - Testcase not applicable REBOOT PERSISTENT STORAGE not supported" -l "tools/device/check_reboot_file_exists.sh" -s

# Reboot file path is hard coded.
# There is no option in OpenSync to configure its location.
reboot_file_path="/var/run/osp_reboot_reason"

if [ -e "$reboot_file_path" ]; then
{
    log "tools/device/check_reboot_file_exists.sh: Reboot file exists '$reboot_file_path'"
    exit 0
}
else
{
    log "tools/device/check_reboot_file_exists.sh: Could not find reboot file at '$reboot_file_path'"
    exit 1
}
fi
