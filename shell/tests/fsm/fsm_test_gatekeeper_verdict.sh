#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat << usage_string
fsm/fsm_test_gatekeeper_verdict.sh [-h] arguments
Description:
    - Script checks logs from the FSM Gatekeeper plugin containing the verdict.
Arguments:
    -h  show this help message
    \$1 (url)              : Url for which verdict is requested   : (string)(required)
    \$2 (expected_verdict) : Expected verdict from the Gatekeeper : (string)(required)
Script usage example:
    ./fsm/fsm_test_gatekeeper_verdict.sh fut.opensync.io/test/url allow
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

# gatekeeper_get_verdict(): verdict for 'http://fut.opensync.io/gatekeeper/test/block' is blocked

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Associated_Clients
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
url=${1}
expected_verdict=${2}

fsm_message_regex="$LOGREAD |
 tail -3000 |
 grep gatekeeper_get_verdict |
 grep ${url} |
 grep 'is ${expected_verdict}'"
wait_for_function_response 0 "${fsm_message_regex}" 5 &&
    log "fsm/fsm_test_gatekeeper_verdict.sh: FSM gatekeeper verdict message found in logs - Success" ||
    raise "Failed to find FSM gatekeeper verdict message in logs, regex used: ${fsm_message_regex} " -l "fsm/fsm_test_gatekeeper_verdict.sh" -tc
