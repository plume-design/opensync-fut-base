#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

dm_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_max_memory.sh [-h]
Description:
    - This script sets max_memory limit in the column other_config of the Node_Services table
Arguments:
    -h  show this help message
    \$1 (max_memory)        : Memory limit in kB for the specified process   : (int)(required)
    \$2 (proc_name)         : Process name : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${dm_setup_file} (see ${dm_setup_file} -h)
    - On DEVICE: Run: ./dm/dm_verify_max_memory.sh <mem_limit> <proc_name>
Script usage example:
    ./dm/dm_verify_max_memory.sh 12000 owm
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "dm/dm_verify_max_memory.sh" -arg
mem_limit=$1
proc_name=$2

log_title "dm/dm_verify_max_memory.sh: DM test - Setting max_memory to ${mem_limit} for process ${proc_name}"


ovsh u Node_Services other_config:del:'["set",["max_memory"]]' -w service==${proc_name}
ovsh u Node_Services other_config:ins:"[\"map\",[[\"max_memory\",\"${mem_limit}\"],[\"max_memory_cnt\",\"1\"]]]" -w service==${proc_name}
exit 0
