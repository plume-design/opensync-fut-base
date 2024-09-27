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
tpsm/tpsm_verify_iperf3_speedtest.sh [-h] arguments
Description:
    - Script verifies iperf3 speedtest feature works on the DUT.
Arguments:
    -h  show this help message
    \$1 (server_ip_addr) : IP address of the server                        : (string)(required)
    \$2 (testid)         : Wifi_Speedtest_Config::testid                   : (int)(required)
    \$3 (upd)            : Run UDP traffic (TCP if false)                  : (bool)(required)
    \$4 (direction)      : DL, UL, DL_UL (default)                         : (string)(optional)(default:"DL_UL")
    \$5 (port)           : port on which iperf3 server is running          : (int)(optional)(default: 5201)
    \$6 (timeout)        : time in seconds to wait for speedtest to finish : (int)(optional)(default: 30)
Testcase procedure:
    - On DEVICE: Run: ./tpsm/tpsm_setup.sh (see tpsm/tpsm_setup.sh -h)
                 Run: ./tpsm/tpsm_verify_iperf3_speedtest.sh <SERVER_IP_ADDRESS> <TRAFFIC_TYPE>
Script usage example:
    ./tpsm/tpsm_verify_iperf3_speedtest.sh fut.opensync.io 123 false DL_UL
    ./tpsm/tpsm_verify_iperf3_speedtest.sh fut.opensync.io 123 true UL 20
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

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -arg
server_ip_addr=${1}
testid=${2}
udp=${3}
direction=${4:-"DL_UL"}
port=${5:-5201}
timeout=${6:-30}

is_dl=false
is_ul=false
case "${direction}" in
    "DL")
        is_dl=true
        ;;
    "UL")
        is_ul=true
        ;;
    "DL_UL")
        is_dl=true
        is_ul=true
        ;;
    *)
        usage && raise "Unsupported argument direction:${direction}. Supported: DL, UL, DL_UL." -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -arg
        ;;
esac

log_title "tpsm/tpsm_verify_iperf3_speedtest.sh: TPSM test - Verify if iperf3 speedtest feature works on the DUT"

empty_ovsdb_table Wifi_Speedtest_Config ||
    raise "Could not empty Wifi_Speedtest_Config: empty_ovsdb_table" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -tc

insert_ovsdb_entry Wifi_Speedtest_Config -i test_type "IPERF3_C" -i testid "${testid}" -i st_server "${server_ip_addr}" -i st_port "${port}" -i st_udp "${udp}" -i st_dir "${direction}" &&
    log "tpsm/tpsm_verify_iperf3_speedtest.sh: insert_ovsdb_entry - Wifi_Speedtest_Config - Success" ||
    raise "insert_ovsdb_entry - Failed to insert Wifi_Speedtest_Config" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -tc

wait_for_function_exit_code 0 "pgrep iperf3" ${timeout}

pid_of_iperf3=$(pgrep "iperf3")
[ -n "$pid_of_iperf3" ] &&
    log "tpsm/tpsm_verify_iperf3_speedtest.sh: Speedtest process started with pid $pid_of_iperf3 - Success" ||
    raise "Speedtest process not started" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -tc

wait_ovsdb_entry Wifi_Speedtest_Status -w testid "$testid" -is testid "$testid" -t ${timeout} &&
    log "tpsm/tpsm_verify_iperf3_speedtest.sh: wait_ovsdb_entry - Wifi_Speedtest_Status::testid $testid - Success" ||
    raise "wait_ovsdb_entry - Wifi_Speedtest_Status::status is not 0" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -tc

check_ovsdb_entry Wifi_Speedtest_Status -w testid "$testid" -w status "0" &&
    log "tpsm/tpsm_verify_iperf3_speedtest.sh: wait_ovsdb_entry - Wifi_Speedtest_Status::status is 0 - Success" ||
    raise "wait_ovsdb_entry - Wifi_Speedtest_Status::status is not 0" -l "tpsm/tpsm_verify_iperf3_speedtest.sh" -tc

if ${is_dl}; then
    wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_Speedtest_Status DL -w testid ${testid}" &&
        log "tpsm/tpsm_verify_iperf3_speedtest.sh: Wifi_Speedtest_Status::DL is set" ||
        log "tpsm/tpsm_verify_iperf3_speedtest.sh: Wifi_Speedtest_Status::DL is empty"
fi

if ${is_ul}; then
    wait_for_function_response 'notempty' "get_ovsdb_entry_value Wifi_Speedtest_Status UL -w testid ${testid}" &&
        log "tpsm/tpsm_verify_iperf3_speedtest.sh: Wifi_Speedtest_Status::UL is set" ||
        log "tpsm/tpsm_verify_iperf3_speedtest.sh: Wifi_Speedtest_Status::UL is empty"
fi

pass
