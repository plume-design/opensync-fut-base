#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

brv_setup_file="brv/brv_setup.sh"
usage()
{
cat << usage_string
brv/brv_is_tool_on_system.sh [-h] arguments
Description:
    - Script checks if the specified tool is present on the system, fails otherwise
Arguments:
    -h : show this help message
    \$1 (builtin_tool) : name of the required tool : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${brv_setup_file} (see ${brv_setup_file} -h)
                 Run: ./brv/brv_is_tool_on_system.sh <TOOL-NAME>
Script usage example:
    ./brv/brv_is_tool_on_system.sh "tail"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "brv/brv_is_tool_on_system.sh" -arg

tool_path=$1

log_title "brv/brv_is_tool_on_system.sh: BRV test - Verify tool '${tool_path}' is present on device"

is_tool_on_system "${tool_path}"
rc=$?
if [ $rc == 0 ]; then
    log "brv/brv_is_tool_on_system.sh: tool '${tool_path}' found on device - Success"
elif [ $rc == 126 ]; then
    raise "Tool '${tool_path}' found on device but could not be invoked - Success" -l "brv/brv_is_tool_on_system.sh" -ec ${rc} -tc
else
    raise "Tool '${tool_path}' could not be found on device" -l "brv/brv_is_tool_on_system.sh" -ec ${rc} -tc
fi

pass
