#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
wpd/wpd_check_flags.sh [-h] arguments
Description:
    - Script validates the WPD input parameters:
        wpd -d, --daemon
        wpd -a, --set-auto
        wpd -n, --set-noauto
        wpd -p, --ping
        wpd -k, --kill
        wpd -v, --verbose
        wpd -x, --proc-name proc name
Arguments:
    -h  show this help message
    \$1 (log_tail_command)     : Command used to tail system logs and store in a separate file : (str)(required)
Script usage example:
    ./wpd/wpd_check_flags.sh 'logread -f'
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
    $(get_process_cmd) | grep wpd
    wpd_service_start >/dev/null 2>&1 || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wpd/wpd_check_flags.sh" -arg
log_tail_command=${1}
WPD_TIMEOUT_WDPING=5
wpd_bin="${OPENSYNC_ROOTDIR}/bin/wpd"

log_title "wpd/wpd_check_flags.sh: WPD test - Validate input flags."

logfile="${FUT_TOPDIR}/logread_$(date -I +"%Y_%m_%d_%H_%M_%S").log"
log "wpd/wpd_check_flags.sh: Start tailing system log to capture WPD log messages and store into ${logfile}."
${log_tail_command} | awk '/WPD/ { print; fflush() }' > ${logfile} &

log "wpd/wpd_check_flags.sh: Ensure WPD is killed."
wpd_process_kill

log "wpd/wpd_check_flags.sh: Testing the --daemon and --proc-name flags: WPD is in daemon mode and an OpenSync process is specified to ping it."
${wpd_bin} --daemon --set-noauto --proc-name cm
sleep 1  # Avoid race conditions
wpd_pid=$(get_pid "${wpd_bin}")
test -n ${wpd_pid} &&
    log "wpd/wpd_check_flags.sh: WPD in daemon mode, PID: ${wpd_pid} - Success" ||
    raise "No WPD in daemon mode" -l "wpd/wpd_check_flags.sh" -tc

log "wpd/wpd_check_flags.sh: Flush logs by killing all background processes."
kill $(jobs -p) >/dev/null 2>&1 || true

log "wpd/wpd_check_flags.sh: Inspecting logs for correct entries."
test_str="Starting WPD (Watchdog Proxy Daemon)"
grep "${test_str}" ${logfile} &&
    log "wpd/wpd_check_flags.sh: Logs contain '${test_str}' - Success" ||
    raise "Logs do not contain ${test_str}" -l "wpd/wpd_check_flags.sh" -tc
test_str="Setting WD timeout to"
grep "${test_str}" ${logfile} &&
    log "wpd/wpd_check_flags.sh: Logs contain '${test_str}' - Success" ||
    raise "Logs do not contain ${test_str}" -l "wpd/wpd_check_flags.sh" -tc
log "wpd/wpd_check_flags.sh: Restart tailing system log to capture WPD log messages and store into ${logfile}."
${log_tail_command} | awk '/WPD/ { print; fflush() }' > ${logfile} &
log "wpd/wpd_check_flags.sh: Wait for $(( WPD_TIMEOUT_WDPING * 2 )) seconds for first ping from external applications."
sleep $(( WPD_TIMEOUT_WDPING * 2 ))
sleep 1  # Avoid race conditions
test_str="Got signal PING"
grep "${test_str}" ${logfile} &&
    log "wpd/wpd_check_flags.sh: Flag --proc-name works. Logs contain '${test_str}' - Success" ||
    raise "Flag --proc-name does not work. Logs do not contain ${test_str}" -l "wpd/wpd_check_flags.sh" -tc

log "wpd/wpd_check_flags.sh: Testing the --set-noauto flag: when OpenSync is stopped, there are no pings to WPD."
log "wpd/wpd_check_flags.sh: Stopping OpenSync."
stop_managers

log "wpd/wpd_check_flags.sh: Clearing ${logfile}."
echo > ${logfile}

log "wpd/wpd_check_flags.sh: Wait for ${WPD_TIMEOUT_WDPING} seconds but there should be no ping."
sleep ${WPD_TIMEOUT_WDPING}
test_str="Got signal PING"
grep "${test_str}" ${logfile} &&
    raise "Flag --set-noauto does not work. Logs contain ${test_str}" -l "wpd/wpd_check_flags.sh" -tc ||
    log "wpd/wpd_check_flags.sh: Flag --set-noauto works. Logs do not contain '${test_str}' - Success"

log "wpd/wpd_check_flags.sh: Clearing ${logfile}."
echo > ${logfile}

log "wpd/wpd_check_flags.sh: Testing the --ping flag: with a WPD in daemon mode and OpenSync stopped, we provide a manual ping."
${wpd_bin} --ping
sleep 1  # Avoid race conditions
test_str="Got signal PING"
grep "${test_str}" ${logfile} &&
    log "wpd/wpd_check_flags.sh: Flag --ping works. Logs contain '${test_str}' - Success" ||
    raise "Flag --ping does not work. Logs do not contain ${test_str}" -l "wpd/wpd_check_flags.sh" -tc

log "wpd/wpd_check_flags.sh: Testing the --kill flag."
${wpd_bin} --kill
wpd_pid=$(get_pid "${wpd_bin}")
test -z ${wpd_pid} &&
    log "wpd/wpd_check_flags.sh: WPD was killed - Success" ||
    raise "WPD was not killed, PID: ${wpd_pid}" -l "wpd/wpd_check_flags.sh" -tc

log "wpd/wpd_check_flags.sh: Clearing ${logfile}."
echo > ${logfile}
log "wpd/wpd_check_flags.sh: Testing the --set-auto and --verbose flags: There should be pings to system watchdog without external applications."
${wpd_bin} --daemon --set-auto --verbose
log "wpd/wpd_check_flags.sh: Wait for ${WPD_TIMEOUT_WDPING} seconds for first ping."
sleep ${WPD_TIMEOUT_WDPING}
sleep 1  # Avoid race conditions
log "wpd/wpd_check_flags.sh: Testing the --set-auto and --verbose flags: There should be additional debug level logs."
test_str="DEBUG.*MISC: cb ping"
grep -E "${test_str}" ${logfile} &&
    log "wpd/wpd_check_flags.sh: Flags --set-auto and --verbose work. Logs contain '${test_str}' - Success" ||
    raise "Flags --set-auto and --verbose do not work. Logs do not contain ${test_str}" -l "wpd/wpd_check_flags.sh" -tc

log "wpd/wpd_check_flags.sh: Starting OpenSync."
start_managers

pass
