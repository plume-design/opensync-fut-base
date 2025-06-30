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
dm/dm_verify_opensync_restart.sh [-h]
Description:
    - Script restarts OpenSync and checks if a crash report file with fields 'name' and 'reason' set to desired values exists in the OpenSync crash directory
Arguments:
    -h  show this help message
    \$1 (crash_name)         : Expected value of the name key in the crash file   : (string)(required)
    \$2 (crash_reason)       : Expected value of the reason key in the crash file : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${dm_setup_file} (see ${dm_setup_file} -h)
    - On DEVICE: Run: ./dm/dm_verify_opensync_restart.sh
Script usage example:
    ./dm/dm_verify_opensync_restart.sh OpenSync "OpenSync restarted by"
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        ls -la "$opensync_crash_dir"
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "dm/dm_verify_opensync_restart.sh" -arg
crash_name=$1
crash_reason=$2

opensync_crash_dir_value=$(get_kconfig_option_value "CONFIG_DM_CRASH_REPORTS_TMP_DIR")
# Clean string of quotes:
opensync_crash_dir=$(echo ${opensync_crash_dir_value} | tr -d '"')

log_title "dm/dm_verify_opensync_restart.sh: DM test - Clean up crash directory '$opensync_crash_dir'"

rm -rf "$opensync_crash_dir"

log_title "dm/dm_verify_opensync_restart.sh: DM test - Trigger OpenSync restart by sending SIGSEGV to the dm.slave process"

pkill -SEGV dm.slave

log_title "dm/dm_verify_opensync_restart.sh: DM test - Periodically check '$opensync_crash_dir' for an OpenSync restart crash file"

PROCESSED_FILES="/tmp/fut_dm_verify_opensync_restart_processed_files"
ELAPSED_TIME=0
INTERVAL=1  # in seconds
TIMEOUT=60  # in seconds
touch "$PROCESSED_FILES"
while sleep $INTERVAL; do
    for file in "$opensync_crash_dir"/*; do
        [ -f "$file" ] || continue

        # Check if file was already checked
        grep -Fxq "$file" "$PROCESSED_FILES" && continue

        # Check for expected values are found in lines starting with name and reason
        if grep -q "^name $crash_name" "$file" && grep -q "^reason .*${crash_reason}" "$file"; then
            log "Valid crash report found: $file"
            rm $PROCESSED_FILES
            exit 0
        else
            log "Crash file found but name and reason do not match: $file"
        fi

        # Mark file as processed
        echo "$file" >> "$PROCESSED_FILES"
    done

    ELAPSED_TIME=$((ELAPSED_TIME + INTERVAL))
    if [ "$ELAPSED_TIME" -ge "$TIMEOUT" ]; then
        break
    fi
done

rm $PROCESSED_FILES
raise "Could not find crash file with matching reason and name within the timeout period" -l "dm/dm_verify_opensync_restart.sh" -tc
