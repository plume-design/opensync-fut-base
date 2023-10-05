#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_count_reboot_status.sh [-h] arguments
Description:
    Validate 'count' field in the Reboot_Status table.
    The test script validates if count field in the Reboot_Status table is being
    recorded correctly and is greater than or equals to 1, considering device
    rebooted at least once in its lifetime.

Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_count_reboot_status.sh
Script usage example:
    ./dm/dm_verify_count_reboot_status.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Reboot_Status
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "dm/dm_verify_count_reboot_status.sh: DM test - Verify 'count' field value in Reboot_Status table is greater than or equals to one."

check_ovsdb_table_exist Reboot_Status &&
    log "dm/dm_verify_count_reboot_status.sh: Reboot_Status table exists in ovsdb - Success" ||
    raise "FAIL: Reboot_Status table does not exist in ovsdb" -l "dm/dm_verify_count_reboot_status.sh" -s

print_tables Reboot_Status

reboot_count_array=$(get_ovsdb_entry_value Reboot_Status count)

for reboot_count in $reboot_count_array; do
    if [ $reboot_count -ge 1 ]; then
        break
    fi
done

if [ $reboot_count -ge 1 ]; then
    log "dm/dm_verify_count_reboot_status.sh: Valid Reboot_Status::count value (i.e, >= 1) found - Success"
else
    raise "FAIL: Invalid Reboot_Status::count value found" -l "dm/dm_verify_count_reboot_status.sh" -tc
fi

pass
