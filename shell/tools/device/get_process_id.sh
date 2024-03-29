#!/bin/sh

# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh > /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh > /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" > /dev/null

usage()
{
cat << usage_string
tools/device/get_process_id.sh [-h] arguments
Description:
    Echoes PIDs of requested processes.

Arguments:
    -h  show this help message
    \$1 (process_names) : Process names : (string)(required)
Script usage example:
    ./tools/device/get_process_id.sh /usr/opensync/bin/wm /usr/opensync/bin/sm
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/get_process_id.sh" -arg

# String to store PIDs
pids=""

# Loop through each argument and pgrep for its PID
for arg do
    wait_for_function_response 0 "pgrep -o '$arg'" > /dev/null
    pid=$(pgrep -o "$arg")
    pids="$pids $arg:$pid"
done

echo "$pids"
