#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh > /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh > /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" > /dev/null
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm > /dev/null
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm > /dev/null

usage()
{
cat << usage_string
tools/device/syslog_rotate.sh [-h]
Description:
    - Script pings the selected IP address and collects the statistics to the specified log file.
Arguments:
    -h  show this help message
    \$1 (log_file)           : Name of the log file                                  : (string)(optional)
    \$2 (logs_archive)       : Path to log archive directory                         : (string)(optional)
    \$3 (syslog_subdir)      : Subdirectory name for syslog in log archive directory : (string)(optional)
    \$4 (rotation_max_files) : Max number of archive files when rotating             : (string)(optional)
    \$5 (logs_location)      : Path to files to be rotated                           : (string)(optional)
Script usage example:
    ./tools/device/syslog_rotate.sh
    ./tools/device/syslog_rotate.sh messages /usr/opensync/log_archive syslog 8 /var/log
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

syslog_rotate_cmd=$(get_syslog_rotate_cmd)
test -n "${syslog_rotate_cmd}" &&
    log "tools/device/syslog_rotate.sh: Syslog rotate script: ${syslog_rotate_cmd}" ||
    raise "Could not find syslog rotate script" -l "tools/device/syslog_rotate.sh" -ds
log "tools/device/syslog_rotate.sh: Rotating system logs."
$syslog_rotate_cmd "$@"
