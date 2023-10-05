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
tools/device/check_lib_plugin_exists.sh [-h] arguments
Description:
    - Script checks existence of FSM Plugin lib file
Arguments:
    -h  show this help message
    \$1 (expected_user_agent) : Plugin lib file path : (string)(required)
Script usage example:
    ./tools/device/check_lib_plugin_exists.sh custom_user_agent
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
plugin_lib_file_path=${1}

log "Checking if FSM Plugin lib file exists"
[ -f "${plugin_lib_file_path}" ] &&
    log "FSM plugin lib ${plugin_lib_file_path} file exists - Success" ||
    raise "Missing ${plugin_lib_file_path} FSM plugin lib file" -tc "tools/device/check_lib_plugin_exists.sh" -s
