#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tpsm/tpsm_verify_ookla_speedtest.sh [-h] arguments
Description:
    - Script verifies ookla Speedtest.
Arguments:
    -h  show this help message
    \$1  (testid)   : Wifi_Speedtest_Config::testid                     : (int)(required)
    \$2  (timeout)  : time in seconds to wait for speedtest to finish   : (int)(optional)(default: 90)
Testcase procedure:
    - On DEVICE: Run: ./tpsm/tpsm_setup.sh (see tpsm/tpsm_setup.sh -h)
                 Run: ./tpsm/tpsm_verify_ookla_speedtest.sh <TESTID>
Script usage example:
    ./tpsm/tpsm_verify_ookla_speedtest.sh 110
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Speedtest_Config Wifi_Speedtest_Status
    empty_ovsdb_table Wifi_Speedtest_Config
    empty_ovsdb_table Wifi_Speedtest_Status
    $(get_process_cmd)
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -arg
testid=${1}
ookla_timeout=${2:-90}

log_title "tpsm/tpsm_verify_ookla_speedtest.sh: TPSM test - Verify Ookla Speedtest"

check_kconfig_option "CONFIG_3RDPARTY_OOKLA" "y" ||
    check_kconfig_option "CONFIG_SPEEDTEST_OOKLA" "y" ||
        raise "OOKLA not present on device" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -s

# ookla_path is hardcoded during compile time
ookla_path="${OPENSYNC_ROOTDIR}/bin/ookla"
[ -e "$ookla_path" ] &&
    log "tpsm/tpsm_verify_ookla_speedtest.sh: ookla speedtest binary is present on system - Success" ||
    raise "Ookla speedtest binary is not present on system" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -s

empty_ovsdb_table Wifi_Speedtest_Config ||
    raise "Could not empty Wifi_Speedtest_Config: empty_ovsdb_table" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -tc

insert_ovsdb_entry Wifi_Speedtest_Config -i test_type "OOKLA" -i testid "$testid" &&
    log "tpsm/tpsm_verify_ookla_speedtest.sh: insert_ovsdb_entry - Wifi_Speedtest_Config::test_type - Success" ||
    raise "insert_ovsdb_entry - Failed to insert Wifi_Speedtest_Config::test_type" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -tc

sleep 1

pid_of_ookla=$(get_pid "$ookla_path")
[ -n "$pid_of_ookla" ] &&
    log "tpsm/tpsm_verify_ookla_speedtest.sh: Speedtest process started with pid $pid_of_ookla - Success" ||
    raise "Speedtest process not started" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -tc

wait_ovsdb_entry Wifi_Speedtest_Status -w testid "$testid" -is status "0" -t ${ookla_timeout} &&
    log "tpsm/tpsm_verify_ookla_speedtest.sh: wait_ovsdb_entry - Wifi_Speedtest_Status::status is 0 - Success" ||
    raise "wait_ovsdb_entry - Wifi_Speedtest_Status::status is not 0" -l "tpsm/tpsm_verify_ookla_speedtest.sh" -tc

wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_Speedtest_Status DL" &&
    log "tpsm/tpsm_verify_ookla_speedtest.sh: Wifi_Speedtest_Status::DL is set" ||
    log "tpsm/tpsm_verify_ookla_speedtest.sh: Wifi_Speedtest_Status::DL is empty"

wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_Speedtest_Status UL" &&
    log "tpsm/tpsm_verify_ookla_speedtest.sh: Wifi_Speedtest_Status::UL is set" ||
    log "tpsm/tpsm_verify_ookla_speedtest.sh: Wifi_Speedtest_Status::UL is empty"

pass
