#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

qm_setup_file="qm/qm_setup.sh"
usage()
{
cat << usage_string
qm/qm_telog_validate.sh [-h] \$1 \$2
Description:
    - Script parses the system logs for time event log messages.
Dependency:
    - Script is dependent on tools 'telog', 'timeout'.
Arguments:
    -h : show this help message
    \$1 (number_of_logs)   : Number of logs produced with the 'telog' CLI tool : (int)(required)
    \$2 (log_tail_command) : The command for tailing system logs               : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${qm_setup_file} (see ${qm_setup_file} -h)
                 Run: ./qm/qm_telog_validate.sh <NUMBER_OF_LOGS> <LOG_TAIL_COMMAND>
Usage:
    ./qm/qm_telog_validate.sh <NUMBER_OF_LOGS> <LOG_TAIL_COMMAND>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

is_tool_on_system "telog" &&
    log "qm/qm_telog_validate.sh: 'telog' tool found on device - Success" ||
    raise "FAIL: Tool 'telog' could not be found on device" -l "qm/qm_telog_validate.sh" -s

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s), provided $#" -l "qm/qm_telog_validate.sh" -arg
number_of_logs=$1
log_tail_command=$2

trap '
    kill $(jobs -p) >/dev/null 2>&1 || true
    rm -f ${logfile}
' EXIT SIGINT SIGTERM

log_title "qm/qm_telog_validate.sh: QM test - Verify telog messages"

telog_name="FUT"
telog_category="test"
telog_subject="shell"
telog_message="Time event log message"
logfile="${FUT_TOPDIR}/logread_$(date -I +"%Y_%m_%d_%H_%M_%S").log"
log "qm/qm_telog_validate.sh: Start tailing system log to capture time event log messages and store into ${logfile}."
rm -f ${logfile}
timeout ${DEFAULT_WAIT_TIME:?} ${log_tail_command} | grep -E "TELOG.*${telog_name}.*${telog_category}.*${telog_subject}.*${telog_message}" > ${logfile} &

log "qm/qm_telog_validate.sh: Generating ${number_of_logs} time event log messages"
telog_sent=0
telog_failed=0
for telog_step in $(seq 1 ${number_of_logs}); do
    timeout 3 telog -n "${telog_name}" -c "${telog_category}" -s "${telog_subject}" -t "${telog_step}" "${telog_message}" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        telog_sent=$((telog_sent+1))
    elif [ $? -ge 124 ]; then
        raise "FAIL: 'telog' call ${telog_step} failed with timeout" -l "qm/qm_telog_validate.sh" -tc
    else
        # regular error is expected when log server is down
        telog_failed=$((telog_failed+1))
    fi
done

log "qm/qm_telog_validate.sh: Waiting a while to flush all time event logs to file."
sleep 5

log "qm/qm_telog_validate.sh: Killing all jobs put in the background by this script."
kill $(jobs -p) >/dev/null 2>&1 || true

log "qm/qm_telog_validate.sh: Check the log file for time event logs."
[ -e ${logfile} ] ||
    raise "FAIL: Log file ${logfile} does not exist." -l "qm/qm_telog_validate.sh" -tc

telog_captured=$(wc -l ${logfile} | cut -d' ' -f1)
logno_min=$((number_of_logs*95/100))
log "qm/qm_telog_validate.sh: Logs issued: ${number_of_logs}, logs sent: ${telog_sent}, logs captured: ${telog_captured}, logs lost: ${telog_failed}."
# TODO: fix logging, then test
[ ${telog_sent} -eq ${telog_captured} ] &&
    log "qm/qm_telog_validate.sh: Number of logs sent: ${telog_sent} matches the number of logs captured: ${telog_captured} - Success" ||
    raise "FAIL: Number of logs sent: ${telog_sent} does not match the number of logs captured: ${telog_captured}" -l "$tc_name" -tc

pass
