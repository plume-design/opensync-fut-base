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
pm/pm_trigger_cloud_logpull.sh [-h] arguments
Description:
    - Validate Cloud trigered logpull event. The test simulates a cloud triggered
      logpull by setting an upload location and upload token in the AW_LM_Config
      table. The logpull service starts collecting system logs, states and current
      configuraton of nodes and creates a tarball. The test also checks if the
      logpull tarball was created by verifying that the directory which includes
      the created tarball is not empty. The logpull tarball is uploaded to the
      specified location, using the upload token as credentials.
Arguments:
    -h  show this help message
    \$1 (upload_location)  : AW_LM_Config::upload_location : (string)(required)
    \$2 (upload_token)     : AW_LM_Config::upload_token : (string)(required)
    \$3 (name)             : AW_LM_Config::name : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./pm/pm_trigger_cloud_logpull.sh <UPLOAD_LOCATION> <UPLOAD_TOKEN> <NAME>
Script usage example:
    ./pm/pm_trigger_cloud_logpull.sh <UPLOAD_LOCATION> <UPLOAD_TOKEN> <NAME>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "pm/pm_verify_log_severity.sh" -arg
upload_location=${1}
upload_token=${2}
aw_lm_config_name=${3}

log_title "pm/pm_trigger_cloud_logpull.sh: LM test - Verify Cloud triggered logpull event"

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables AW_Debug AW_LM_Config
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

is_logpull_dir_empty &&
    log "pm/pm_trigger_cloud_logpull.sh: Logpull directory is empty - Success" ||
    empty_logpull_dir

empty_ovsdb_table AW_Debug &&
    log -deb "pm/pm_trigger_cloud_logpull.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty table:" -l "pm/pm_trigger_cloud_logpull.sh" -ds

log "pm/pm_trigger_cloud_logpull.sh: For PM set log severity to DEBUG"
set_manager_log PM TRACE &&
    log "pm/pm_trigger_cloud_logpull.sh - set_manager_log PM DEBUG - Success" ||
    raise "set_manager_log PM DEBUG" -l "pm/pm_trigger_cloud_logpull.sh" -tc

empty_ovsdb_table AW_LM_Config &&
    log -deb "pm/pm_trigger_cloud_logpull.sh - AW_LM_Config table emptied - Success" ||
    raise "empty_ovsdb_table AW_LM_Config - Could not empty table:" -l "pm/pm_trigger_cloud_logpull.sh" -ds

# Wait a bit for the setting to be applied
sleep 1

insert_ovsdb_entry AW_LM_Config \
    -i upload_location "${upload_location}" \
    -i upload_token "${upload_token}" \
    -i name "${aw_lm_config_name}" &&
        log "pm/pm_trigger_cloud_logpull.sh: AW_LM_Config values inserted - Success" ||
        raise "Failed to insert_ovsdb_entry" -l "pm/pm_trigger_cloud_logpull.sh" -fc

check_pm_report_log &&
    log "pm/pm_trigger_cloud_logpull.sh: PM logpull log found - Success" ||
    raise "PM logpull log not found" -l "pm/pm_trigger_cloud_logpull.sh" -tc

# By checking that the logpull directory is not empty, we can verify that the logpull tarball was successfully generated
wait_for_function_exit_code 1 "is_logpull_dir_empty" &&
    log "pm/pm_trigger_cloud_logpull.sh: Logpull directory is not empty - Success" ||
    raise "Logpull directory is empty" -l "pm/pm_trigger_cloud_logpull.sh" -tc

# By checking that the logpull directory is empty, we can verify that the
# logpull tarball was deleted after it was sent to the upload location
wait_for_function_exit_code 0 "is_logpull_dir_empty" 10 10 &&
    log "pm/pm_trigger_cloud_logpull.sh: Logpull directory is empty - Success" ||
    raise "Logpull directory is not empty" -l "pm/pm_trigger_cloud_logpull.sh" -tc

pass
