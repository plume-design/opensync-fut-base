#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   PP203X libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/pp203x_lib_override.sh sourced"

####################### UNIT OVERRIDE SECTION - START #########################

###############################################################################
# DESCRIPTION:
#   Function disables watchdog.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   None.
# USAGE EXAMPLE(S):
#   disable_watchdog
###############################################################################
disable_watchdog()
{
    log -deb "pp203x_lib_override:disable_watchdog - Disabling watchdog"
    ${OPENSYNC_ROOTDIR}/bin/wpd --set-auto
    sleep 1
    # shellcheck disable=SC2034
    PID=$(pidof wpd) || raise "wpd not running" -l "pp203x_lib_override:disable_watchdog" -ds
}

###############################################################################
# DESCRIPTION:
#   Function checks if device supports WPA3
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   1   WPA3 incompatible.
#   0   WPA3 compatible.
# USAGE EXAMPLE(S):
#   check_wpa3_compatibility
###############################################################################
check_wpa3_compatibility()
{
    check_kconfig_option "CONFIG_PLATFORM_QCA_QSDK110" "y" &&
        log -deb "pp203x_lib_override:check_wpa3_compatibility - WPA3 compatible" ||
        log -err "pp203x_lib_override:check_wpa3_compatibility - WPA3 incompatible"
}

###############################################################################
# DESCRIPTION:
#   Function initializes device for use in FUT.
#   It disables watchdog to prevent the device from rebooting.
#   It stops healthcheck service to prevent the device from rebooting.
#   It calls a function that instructs CM to prevent the device from rebooting.
#   It stops all managers.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   device_init
###############################################################################
device_init()
{
    disable_watchdog &&
        log -deb "pp203x_lib_override:device_init - Watchdog disabled - Success" ||
        raise "FAIL: device_init - Could not disable watchdog" -l "pp203x_lib_override:device_init" -ds

    stop_managers &&
        log -deb "pp203x_lib_override:device_init - Managers stopped - Success" ||
        raise "FAIL: stop_managers - Could not stop managers" -l "pp203x_lib_override:device_init" -ds

    stop_healthcheck &&
        log -deb "pp203x_lib_override:device_init - Healthcheck stopped - Success" ||
        raise "FAIL: stop_healthcheck - Could not stop healthcheck" -l "pp203x_lib_override:device_init" -ds

    disable_fatal_state_cm &&
        log -deb "pp203x_lib_override:device_init - CM fatal state disabled - Success" ||
        raise "FAIL: disable_fatal_state_cm - Could not disable CM fatal state" -l "pp203x_lib_override:device_init" -ds

    return $?
}

####################### UNIT OVERRIDE SECTION - STOP ##########################

####################### CERTIFICATE OVERRIDE SECTION - START ##################

###############################################################################
# DESCRIPTION:
#   Function compares CN(Common Name) of the certificate to several parameters:
#   device model string, device id, WAN eth port MAC address.
#   NOTE: CN verification is optional, this function just echoes these
#         parameters. If the validation should be required, please overload the
#         function in the device shell library overload file.
# INPUT PARAMETER(S):
#   $1  Common Name stored in the certificate (string, required)
#   $2  Device model string (string, optional)
#   $3  Device id (string, optional)
#   $4  MAC address of device WAN eth port (string, optional)
# RETURNS:
#   0   CN matches any input parameter
#   1   CN mismatches all input parameters
# USAGE EXAMPLE(S):
#   check_certificate_cn 1A2B3C4D5E6F 1A2B3C4D5E6F PP203X 00904C324057
###############################################################################
check_certificate_cn()
{
    local NARGS=1
    [ $# -lt ${NARGS} ] &&
        raise "pp203x_lib_override:check_certificate_cn requires at least ${NARGS} input argument(s), $# given" -arg
    comm_name=${1}
    device_model=${2}
    device_id=${3}
    wan_eth_mac_string=$(echo "$4" | sed -e 's/://g' | tr '[:lower:]' '[:upper:]')

    [ "$comm_name" = "$device_model" ] &&
        echo "Common Name of certificate: $comm_name matches device model: $device_model" && return 0
    [ "$comm_name" = "$device_id" ] &&
        echo "Common Name of certificate: $comm_name matches device ID: $device_id" && return 0
    [ "$comm_name" = "$wan_eth_mac_string" ] &&
        echo "Common Name of certificate: $comm_name matches device WAN eth MAC address: $wan_eth_mac_string" && return 0

    return 1
}

####################### CERTIFICATE OVERRIDE SECTION - STOP ###################
