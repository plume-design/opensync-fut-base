#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh > /dev/null
. /tmp/fut-base/shell/config/default_shell.sh > /dev/null
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh" > /dev/null
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm > /dev/null
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm > /dev/null

usage()
{
cat << usage_string
tools/device/syslog_rotate.sh [-h]
Description:
    - Script rotates the system logs. This is used to remove unnecessary logs during test steps.
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

device_syslog_rotate "$@"
