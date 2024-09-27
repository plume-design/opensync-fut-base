#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
wpd/wpd_stop_opensync.sh [-h] arguments
Description:
    - Script stops OpenSync and verifies if WPD will attempt to reboot the device after a set time.
Arguments:
    -h  show this help message
    \$1 (wpd_ping_timeout) : Stop pinging watchdog if there is no ping from external applications for the last x seconds : (int)(required)
    \$2 (log_tail_command) : Command used to tail system logs and store in a separate file                               : (str)(required)
Script usage example:
    ./wpd/wpd_stop_opensync.sh 60 'logread -f'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    cat ${logfile} || true
    rm -f ${FUT_TOPDIR}/logread_*
    kill $(jobs -p) >/dev/null 2>&1 || true
    wpd_service_start >/dev/null 2>&1 || true
    $(get_process_cmd) | grep wpd || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wpd/wpd_stop_opensync.sh" -arg
wpd_ping_timeout=${1}
log_tail_command=${2}
WPD_TIMEOUT_WDPING=5
wpd_bin="${OPENSYNC_ROOTDIR}/bin/wpd"

log_title "wpd/wpd_stop_opensync.sh: WPD test - Reboot device when stopping OpenSync."

logfile="${FUT_TOPDIR}/logread_$(date -I +"%Y_%m_%d_%H_%M_%S").log"
log "wpd/wpd_stop_opensync.sh: Start tailing system log to capture WPD log messages and store into ${logfile}."
rm -f ${logfile}
${log_tail_command} | awk '/WPD/ { print; fflush() }' > ${logfile} &

log "wpd/wpd_stop_opensync.sh: Ensure WPD is started."
wpd_service_start

log "wpd/wpd_stop_opensync.sh: Wait for ${WPD_TIMEOUT_WDPING} seconds for first ping."
sleep ${WPD_TIMEOUT_WDPING}
sleep 1  # Avoid race conditions

pre_cmd_time=$(date +%s)
log "wpd/wpd_stop_opensync.sh: Stopping OpenSync."
stop_managers
log "wpd/wpd_stop_opensync.sh: Issue ping and wait for ${wpd_ping_timeout} seconds for WPD to timeout."
${wpd_bin} --ping
sleep ${wpd_ping_timeout}
sleep 1  # Avoid race conditions

log "wpd/wpd_check_flags.sh: Ensure WPD is killed."
wpd_process_kill

log "wpd/wpd_stop_opensync.sh: Ensure WPD is started."
wpd_service_start
log "wpd/wpd_stop_opensync.sh: Issue ping to prevent WPD timeout and system watchdog from biting."
${wpd_bin} --ping

log "wpd/wpd_stop_opensync.sh: Starting OpenSync."
start_managers

log "wpd/wpd_stop_wpd.sh: System watchdog did not reset the system for ${wpd_ping_timeout} seconds."

log "wpd/wpd_check_flags.sh: Flush logs by killing all background processes."
kill $(jobs -p) >/dev/null 2>&1 || true

log "wpd/wpd_stop_opensync.sh: Inspecting logs for correct entries."
test_str="Failed to get ping from managers. Watchdog will soon bite"
grep "${test_str}" ${logfile} &&
    log "wpd/wpd_stop_opensync.sh: Logs contain ${test_str} - Success" ||
    raise "Logs do not contain ${test_str}" -l "wpd/wpd_stop_opensync.sh" -tc
test_str="Setting WD timeout to 3 seconds"
grep "${test_str}" ${logfile} &&
    log "wpd/wpd_stop_opensync.sh: Logs contain ${test_str} - Success" ||
    raise "Logs do not contain ${test_str}" -l "wpd/wpd_stop_opensync.sh" -tc

pass
