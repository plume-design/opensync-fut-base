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
dm/dm_verify_counter_inc_reboot_status.sh [-h] arguments
Description:
    The test script checks if count is incremented and reboot type is USER after reboot
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_counter_inc_reboot_status.sh <COUNT_BEFORE_REBOOT> <COUNT_AFTER_REBOOT>
Script usage example:
    ./dm/dm_verify_counter_inc_reboot_status.sh 121 122
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

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "dm/dm_verify_counter_inc_reboot_status.sh" -arg
count_before_reboot=$1
count_after_reboot=$2

log_title "dm/dm_verify_counter_inc_reboot_status.sh: DM test - Verify Reboot_Status::count is incremented and reboot type is USER"

count_to_check=$(($count_before_reboot+1))
if [ $count_after_reboot -eq $count_to_check ]; then
    log "dm/dm_verify_counter_inc_reboot_status.sh: Reboot_Status::count field is incremented - Success"
    wait_for_function_response 0 "check_ovsdb_entry Reboot_Status -w count $count_after_reboot -w type 'USER'" &&
        log "dm/dm_verify_counter_inc_reboot_status.sh: Reboot counter incremented from ${count_before_reboot} to ${count_after_reboot} after reboot - Success"
else
    raise "FAIL: Reboot_Status::count field failed to increment ${count_before_reboot} -> ${count_after_reboot}" -l "dm/dm_verify_counter_inc_reboot_status.sh" -tc
fi

pass
