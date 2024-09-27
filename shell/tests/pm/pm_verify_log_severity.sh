#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="pm/pm_setup.sh"
usage()
{
cat << usage_string
pm/pm_verify_log_severity.sh [-h] arguments
Description:
    - Validate dynamic changes to log severity during device runtime. The test
      sets log severity for service in AW_Debug table and checks the content of
      the file, determined by the Kconfig option TARGET_PATH_LOG_STATE value.
Arguments:
    -h  show this help message
    \$1 (name)         : Name of the service or manager in AW_Debug::name : (string)(required)
    \$2 (log_severity) : Log severity level in AW_Debug::log_severity     : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./pm/pm_verify_log_severity.sh <NAME> <LOG_SEVERITY>
Script usage example:
    ./pm/pm_verify_log_severity.sh SM TRACE
    ./pm/pm_verify_log_severity.sh FSM DEBUG
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "pm/pm_verify_log_severity.sh" -arg
name=${1}
log_severity=${2}

log_title "pm/pm_verify_log_severity.sh: LM test - Verify dynamic changes to log severity during device runtime"

log_state_value=$(get_kconfig_option_value "TARGET_PATH_LOG_STATE")
# Clean string of quotes:
log_state_file=$(echo ${log_state_value} | tr -d '"')
[ -z ${log_state_file} ] && raise "Kconfig option TARGET_PATH_LOG_STATE has no value" -l "pm/pm_verify_log_severity.sh" -arg
# Trap needs to come after "log_state_file"
trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    cat $log_state_file
    print_tables AW_Debug
    empty_ovsdb_table AW_Debug
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log "pm/pm_verify_log_severity.sh: Test setup - clean AW_Debug table"
empty_ovsdb_table AW_Debug  &&
    log "pm/pm_verify_log_severity.sh - AW_Debug table empty - Success" ||
    raise "Could not empty table: empty_ovsdb_table AW_Debug" -l "pm/pm_verify_log_severity.sh" -ds

log "pm/pm_verify_log_severity.sh: Set log severity ${log_severity} for ${name}"
set_manager_log ${name} ${log_severity} &&
    log "pm/pm_verify_log_severity.sh - set_manager_log ${name} ${log_severity} - Success" ||
    raise "set_manager_log ${name} ${log_severity}" -l "pm/pm_verify_log_severity.sh" -tc

log "pm/pm_verify_log_severity.sh: Ensure ${log_state_file} exists"
[ -f ${log_state_file} ] &&
    log "pm/pm_verify_log_severity.sh - File ${log_state_file} exists - Success" ||
    raise "File ${log_state_file} does not exist" -l "pm/pm_verify_log_severity.sh" -tc

log "pm/pm_verify_log_severity.sh: Ensure content of ${log_state_file} is correct"
#   ":a"        create a label
#   "N"         append the current and next line to the pattern space
#   "$!ba"      branch to label if not on last line
#   's/\n/ /g'  substitute newline with space for the whole file, get one line
#   's/}/}\n/g' break line at every "}", get json dicts in single lines
sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e 's/}/}\n/g' ${log_state_file} | grep ${name} | grep ${log_severity} &&
    log "pm/pm_verify_log_severity.sh - ${log_state_file} contains ${name}:${log_severity} - Success" ||
    raise "${log_state_file} does not contain ${name}:${log_severity}" -l "pm/pm_verify_log_severity.sh" -tc
# Alternative, drawback: will match if individual lines are present, but not related!
# sed -n -e '/'${name}'/,/log_severity/ p' ${log_state_file} | grep ${log_severity}

pass
