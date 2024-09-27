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
brv/brv_busybox_builtins.sh [-h] arguments
Description:
    - Script checks if the specified tool is busybox builtin tool, fails otherwise
Arguments:
    -h : show this help message
    \$1 (builtin_tool) : name of the required busybox built-in tool : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${brv_setup_file} (see ${brv_setup_file} -h)
                 Run: ./brv/brv_busybox_builtins.sh <TOOL-NAME>
Script usage example:
    ./brv/brv_busybox_builtins.sh "tail"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "brv/brv_busybox_builtins.sh" -arg

builtin_tool=$1

log_title "brv/brv_busybox_builtins.sh: BRV test - Verify '${builtin_tool}' is built into busybox"

is_tool_on_system "busybox"
rc=$?
if [ $rc != 0 ]; then
    raise "Refusing tool search, busybox is not present on system" -l "brv/brv_busybox_builtins.sh" -fc
fi
is_busybox_builtin "${builtin_tool}"
rc=$?
if [ $rc == 0 ]; then
    log "brv/brv_busybox_builtins.sh: '${builtin_tool}' is built into busybox - Success"
else
    raise "'${builtin_tool}' is not built into busybox" -l "brv/brv_busybox_builtins.sh" -tc
fi

pass
