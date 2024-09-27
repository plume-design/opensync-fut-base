#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   BCM947622DVT libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/bcm947622dvt_lib_override.sh sourced"

####################### UNIT OVERRIDE SECTION - START #########################
###############################################################################
# DESCRIPTION:
#   Function rotates the system logs. It is unique to this device, due to the
#   use of the calling function, which takes input parameters.
# INPUT PARAMETER(S):
#   $1  Name of the system log file (string, optional, default: messages)
# RETURNS:
#   0   System log was successfully rotated.
# USAGE EXAMPLE(S):
#   bcm947622dvt_syslog_rotate
#   bcm947622dvt_syslog_rotate messages
###############################################################################
bcm947622dvt_syslog_rotate()
{
    log_file=${1:-messages}
    syslog_path=$(find /var/log -name ${log_file})
    test -n "${syslog_path}" &&
        log "bcm947622dvt_lib_override:bcm947622dvt_syslog_rotate - Syslog path: ${syslog_path}" ||
        raise "Could not find syslog path" -l "bcm947622dvt_lib_override:bcm947622dvt_syslog_rotate -" -ds
    echo > ${syslog_path}
}

###############################################################################
# DESCRIPTION:
#   Function initializes device for use in FUT.
#   It disables watchdog to prevent the device from rebooting.
#   It stops healthcheck service to prevent the device from rebooting.
#   It calls a function that instructs CM to prevent the device from rebooting.
#   It stops all managers.
#   It ensures that the "/etc" folder is writable.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   device_init
###############################################################################
device_init()
{
    disable_fatal_state &&
        log -deb "bcm947622dvt_lib_override:device_init - CM fatal state disabled - Success" ||
        raise "Could not disable CM fatal state" -l "bcm947622dvt_lib_override:device_init" -ds
    log_state_value="$(get_kconfig_option_value "TARGET_PATH_LOG_STATE")"
    log_state_file=$(echo ${log_state_value} | tr -d '"')
    log_dir="${log_state_file%/*}"
    [ -n "${log_dir}" ] || raise "Kconfig option TARGET_PATH_LOG_STATE value empty" -l "bcm947622dvt_lib_override:device_init" -ds
    set_dir_to_writable "${log_dir}" &&
        log -deb "bcm947622dvt_lib_override:device_init - ${log_dir} is writable - Success" ||
        raise "${log_dir} is not writable" -l "bcm947622dvt_lib_override:device_init" -ds
}

###############################################################################
# DESCRIPTION:
#   Function checks if device supports WPA3
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   Always.
# USAGE EXAMPLE(S):
#   check_wpa3_compatibility
###############################################################################
check_wpa3_compatibility()
{
    log -deb "bcm947622dvt_lib_override:check_wpa3_compatibility - WPA3 compatible"
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function echoes the path to the syslog rotate script, or in this case there
#   is no script so the command that does the same thing.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Echoes the command that rotates the syslog file.
# USAGE EXAMPLE(S):
#   get_syslog_rotate_cmd
###############################################################################
get_syslog_rotate_cmd()
{
    echo "bcm947622dvt_syslog_rotate"
}
####################### UNIT OVERRIDE SECTION - STOP ##########################
