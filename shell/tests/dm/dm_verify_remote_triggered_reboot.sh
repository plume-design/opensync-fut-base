#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_remote_triggered_reboot.sh [-h] arguments
Description:
    The test script triggers a remote reboot and verifies that the system reboots after 10s.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_remote_triggered_reboot.sh <DELAYED_REBOOT_SCRIPT_PATH>
Script usage example:
    ./dm/dm_verify_remote_triggered_reboot.sh "/usr/opensync/scripts/delayed-reboot"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Test_Config
    print_tables Reboot_Status
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "dm/dm_verify_remote_triggered_reboot.sh" -arg
delayed_reboot_script_path=$1

reboot_delay_time=10

# Clear Reboot_Status table so that we can check if the device reboots in the next test step
log -deb "dm/dm_verify_remote_triggered_reboot.sh - Clearing Reboot_Status table"
empty_ovsdb_table Reboot_Status &&
    log -deb "dm/dm_verify_remote_triggered_reboot.sh - Reboot_Status table is cleared" ||
    raise "empty_ovsdb_table Reboot_Status" -l "dm/dm_verify_remote_triggered_reboot.sh" -fc

log_title "dm/dm_verify_remote_triggered_reboot.sh: DM test - Verify remote triggered reboot"

params="[\"map\",[[\"arg\",\"10 false\"], [\"path\",\"$delayed_reboot_script_path\"]]]"
insert_ovsdb_entry Wifi_Test_Config -i params "$params" -i test_id reboot ||
    raise "insert_ovsdb_entry Wifi_Test_Config" -l "dm/dm_verify_remote_triggered_reboot.sh" -fc

# sleep for reboot_delay_time + 5 seconds to allow the system to reboot
sleep $(( reboot_delay_time + 5 ))

# if the system did not reboot, the script will return 1
raise "device did not reboot in the expected time" -l "dm/dm_verify_remote_triggered_reboot.sh" -tc
