#!/bin/sh

set -x

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
tpsm/tpsm_crash_speedtest_verify_reporting.sh [-h] arguments
Description:
    - Script configures speedtest, crashes the process and verifies error reporting.
Arguments:
    -h  show this help message
    (test_type)   : Wifi_Speedtest_Config::test_type    : (string)(required)
    (testid)      : Wifi_Speedtest_Config::testid       : (string)(optional)(defauls to 123)
    (timeout)     : Wifi_Speedtest_Config::if_name      : (int)(optional)(defaults to 90)
    (kconfig)     : Check kconfig value is "==y"        : (string)(optional)
    (node_config) : Enable process in Node_Config table : (bool)(optional)(defaults to false)
    (*)           : Any Wifi_Speedtest_Config field     : (any)(optional)
Script usage example:
    ./tpsm/tpsm_crash_speedtest_verify_reporting.sh -test_type OOKLA -testid 123 -kconfig CONFIG_3RDPARTY_OOKLA
    ./tpsm/tpsm_crash_speedtest_verify_reporting.sh -test_type IPERF3_C -testid 456 -timeout 30 -st_dir DL -st_server fut.opensync.io -st_port 5201
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

speedtest_args=""
# Parsing arguments passed to the script.
while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -test_type)
            test_type=${1}
            shift
            ;;
        -testid)
            testid=${1}
            shift
            ;;
        -timeout)
            timeout=${1}
            shift
            ;;
        -kconfig)
            kconfig=${1}
            shift
            ;;
        -node_config)
            node_config=${1}
            shift
            ;;
        -*)
            speedtest_args="${speedtest_args} -i ${option#?} ${1}"
            shift
            ;;
        *)
            raise "Unsupported argument provided: $option" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -arg
            ;;
    esac
done

timeout="${timeout:-90}"
testid="${testid:-123}"
case "${test_type}" in
    "OOKLA")
        process_name="ookla"
        ;;
    "IPERF3_C")
        process_name="iperf3"
        ;;
    *)
        usage && raise "Unsupported argument test_type:${test_type}. Supported: OOKLA, IPERF3_C." -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -arg
        ;;
esac

if [ -n "${kconfig}" ]; then
    check_kconfig_option ${kconfig} "y" ||
        raise "${process_name} feature not supported on this device" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -s
fi

log_title "tpsm/tpsm_crash_speedtest_verify_reporting.sh: TPSM test - Crash speedtest process on the DUT and verify error reporting"

if [ -n "${node_config}" ]; then
    ${OVSH} U Node_Config -w module==${node_config} value:=\"true\" key:=enable
        log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: ovsh Upsert - Node_Config - Success" ||
        raise "ovsh Upsert - Failed to insert Node_Config" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -fc

    wait_ovsdb_entry Node_State -w module "${node_config}" -is value \"true\" -is key enable &&
        log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: wait_ovsdb_entry - Node_State::value and Node_State::key are updated - Success" ||
        raise "wait_ovsdb_entry - Node_State::value and Node_State::key failed to update" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc
fi

empty_ovsdb_table Wifi_Speedtest_Config ||
    raise "Could not empty Wifi_Speedtest_Config: empty_ovsdb_table" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc

insert_ovsdb_entry Wifi_Speedtest_Config -i test_type "${test_type}" -i testid "${testid}" ${speedtest_args} &&
    log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: insert_ovsdb_entry - Wifi_Speedtest_Config - Success" ||
    raise "insert_ovsdb_entry - Failed to insert Wifi_Speedtest_Config" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc

wait_for_function_exit_code 0 "pgrep ${process_name}" ${timeout}
proc_pid=$(pgrep ${process_name})
[ -n "${proc_pid}" ] &&
    log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: Speedtest process ${process_name} started with pid $proc_pid - Success" ||
    raise "Speedtest process ${process_name} not started" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc

wait_ovsdb_entry Wifi_Speedtest_Status -w testid "$testid" -is testid "$testid" -t ${timeout} &&
    log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: wait_ovsdb_entry - Wifi_Speedtest_Status::testid $testid - Success" ||
    raise "wait_ovsdb_entry - Wifi_Speedtest_Status::status is not 0" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc

# Enforce condition is NOT true, wait for 1s is similar to get instantly
wait_ovsdb_entry Wifi_Speedtest_Status -w testid "$testid" -wn status "0" -t 1 &&
    log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: wait_ovsdb_entry - Wifi_Speedtest_Status::status is not 0 - Success" ||
    raise "wait_ovsdb_entry - Wifi_Speedtest_Status::status is 0" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc

if [ -n "${node_config}" ]; then
    remove_ovsdb_entry Node_Config -w module ${node_config} &&
        log "tpsm/tpsm_crash_speedtest_verify_reporting.sh: remove_ovsdb_entry - Removed module ${process_name} from Node_Config table - Success" ||
        raise "remove_ovsdb_entry - Failed to remove module ${process_name} from Node_Config table" -l "tpsm/tpsm_crash_speedtest_verify_reporting.sh" -tc
fi

pass
