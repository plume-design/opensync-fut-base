#!/bin/sh

# FUT environment loading
# Script echoes single line so we are redirecting source output to /dev/null
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh &> /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" &> /dev/null
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -n "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

manager_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
tools/device/get_count_reboot_status.sh [-h] arguments
Description:
    Echoes recent 'count' field in the Reboot_Status table.

Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./tools/device/get_count_reboot_status.sh
Script usage example:
    ./tools/device/get_count_reboot_status.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_OSP_REBOOT_PSTORE" "y" &> /dev/null ||
    raise "CONFIG_OSP_REBOOT_PSTORE != y - Testcase not applicable REBOOT PERSISTENT STORAGE not supported" -l "tools/device/get_count_reboot_status.sh" -s

reboot_count_array=$(${OVSH} s Reboot_Status count -r)

recent_reboot_count=0
for reboot_count in $reboot_count_array; do
    if [ $reboot_count -gt $recent_reboot_count ]; then
        recent_reboot_count=$reboot_count
    fi
done

echo "${recent_reboot_count}"
