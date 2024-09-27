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
tools/device/check_channel_is_ready.sh [-h] arguments
Description:
    - Script runs wm2_lib::check_is_channel_ready_for_use with given parameters
Arguments:
    -h  show this help message
    - \$1 (channel)           : Channel to check  : (integer)(required)
    - \$2 (radio_interface)   : radio interface   : (string)(required)
Script usage example:
    ./tools/device/check_channel_is_ready.sh 6 wifi0
See wm2_lib::check_is_channel_ready_for_use for more information
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "tools/device/$(basename "$0"): check_channel_is_ready - Check if channel on the interface is ready for use"

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables Wifi_Radio_State
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg

channel=${1}
radio=${2}
wait_for_function_response 0 "check_is_channel_ready_for_use $channel $radio" &&
    log "tools/device/check_channel_is_ready.sh: check_is_channel_ready_for_use - Success" ||
    raise "check_is_channel_ready_for_use - Failed" -l "tools/device/check_channel_is_ready.sh" -tc

exit 0
