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
    stop_managers &&
        log -deb "bcm947622dvt_lib_override:device_init - Managers stopped - Success" ||
        raise "FAIL: Could not stop managers" -l "bcm947622dvt_lib_override:device_init" -ds
    stop_healthcheck &&
        log -deb "bcm947622dvt_lib_override:device_init - Healthcheck stopped - Success" ||
        raise "FAIL: Could not stop healthcheck" -l "bcm947622dvt_lib_override:device_init" -ds
    disable_fatal_state_cm &&
        log -deb "bcm947622dvt_lib_override:device_init - CM fatal state disabled - Success" ||
        raise "FAIL: Could not disable CM fatal state" -l "bcm947622dvt_lib_override:device_init" -ds
    log_state_value="$(get_kconfig_option_value "TARGET_PATH_LOG_STATE")"
    log_state_file=$(echo ${log_state_value} | tr -d '"')
    log_dir="${log_state_file%/*}"
    [ -n "${log_dir}" ] || raise "Kconfig option TARGET_PATH_LOG_STATE value empty" -l "bcm947622dvt_lib_override:device_init" -ds
    set_dir_to_writable "${log_dir}" &&
        log -deb "bcm947622dvt_lib_override:device_init - ${log_dir} is writable - Success" ||
        raise "FAIL: ${log_dir} is not writable" -l "bcm947622dvt_lib_override:device_init" -ds
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

####################### UNIT OVERRIDE SECTION - STOP ##########################
