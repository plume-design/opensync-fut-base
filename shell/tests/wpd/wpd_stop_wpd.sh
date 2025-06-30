#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
wpd/wpd_stop_wpd.sh [-h] arguments
Description:
    - Script stops WPD and verifies if system watchdog will reset the system after the preset timeout.
Arguments:
    -h  show this help message
    \$1 (wpd_watchdog_timeout) : Time after last ping when system watchdog resets the system   : (int)(required)
Script usage example:
    ./wpd/wpd_stop_wpd.sh 30
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    $(get_process_cmd) | grep wpd || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wpd/wpd_stop_wpd.sh" -arg
wpd_watchdog_timeout=${1}

log_title "wpd/wpd_stop_wpd.sh: WPD test - Reboot device when killing WPD."

# Some chips have HW watchdog tied to CPU clock. This is a generic workaround for this limitation for multi-core CPUs.
log "wpd/wpd_stop_wpd.sh: Causing high load on one CPU core."
nice -n -20 md5sum /dev/zero &  # CPU burn one core

log "wpd/wpd_stop_wpd.sh: Ensure WPD is started."
wpd_service_start

log "wpd/wpd_stop_wpd.sh: Ensure WPD is killed."
wpd_process_kill

log "wpd/wpd_stop_wpd.sh: Watchdog should bite in ${wpd_watchdog_timeout} seconds, waiting for $(( wpd_watchdog_timeout - 5 )) seconds."
sleep $(( wpd_watchdog_timeout - 5 ))

log "wpd/wpd_stop_wpd.sh: System watchdog did not reset the system for ${wpd_watchdog_timeout} seconds."

log "wpd/wpd_stop_wpd.sh: Letting system watchdog reset the system."

log "wpd/wpd_stop_wpd.sh: Flush logs by killing all background processes."
# CPU burn should also be killed here
jobs -p | xargs -r kill >/dev/null 2>&1 || true

pass
