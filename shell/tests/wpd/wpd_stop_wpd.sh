#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

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

log "wpd/wpd_stop_wpd.sh: Ensure WPD is started."
wpd_service_start

log "wpd/wpd_stop_wpd.sh: Ensure WPD is killed."
wpd_process_kill

log "wpd/wpd_stop_wpd.sh: Watchdog should bite in ${wpd_watchdog_timeout} seconds, waiting for $(( wpd_watchdog_timeout - 1 )) seconds."
sleep $(( wpd_watchdog_timeout - 1 ))

log "wpd/wpd_stop_wpd.sh: System watchdog did not reset the system for ${wpd_watchdog_timeout} seconds."

log "wpd/wpd_stop_wpd.sh: Letting system watchdog reset the system."

pass
