#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   IPQ807X_AP_HK09 libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/ipq807x_ap_hk09_lib_override.sh sourced"

####################### UNIT OVERRIDE SECTION - START #########################

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
    stop_managers &&
        log -deb "ipq807x_ap_hk09_lib_override:device_init - Managers stopped - Success" ||
        raise "FAIL: stop_managers - Could not stop managers" -l "ipq807x_ap_hk09_lib_override:device_init" -ds

    stop_healthcheck &&
        log -deb "ipq807x_ap_hk09_lib_override:device_init - Healthcheck stopped - Success" ||
        raise "FAIL: stop_healthcheck - Could not stop healthcheck" -l "ipq807x_ap_hk09_lib_override:device_init" -ds

    disable_fatal_state_cm &&
        log -deb "ipq807x_ap_hk09_lib_override:device_init - CM fatal state disabled - Success" ||
        raise "FAIL: disable_fatal_state_cm - Could not disable CM fatal state" -l "ipq807x_ap_hk09_lib_override:device_init" -ds

    return $?
}

###############################################################################
# DESCRIPTION:
#   Function returns HT mode set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
#   $2  channel (int, not used, but still required, do not optimize)
# RETURNS:
#   Echoes HT mode set for interface
# USAGE EXAMPLE(S):
#   get_ht_mode_from_os home-ap-24 1
###############################################################################
get_ht_mode_from_os()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "ipq807x_ap_hk09_lib_override:get_ht_mode_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1
    channel=$2

    iwpriv $vif_if_name get_mode | sed 's/HE/ HT/g' | sed 's/PLUS$//' | sed 's/MINUS$//' | awk '{ print $3 }'
}

###############################################################################
# DESCRIPTION:
#   Function echoes actual chainmask of the radio. Actual chainmask info
#   is stored in the higher nibble.
# INPUT PARAMETER(S):
#   $1  Chainmask of the radio (int, required)
#   $2  Frequency band of the radio (string, required)
# RETURNS:
#   Transformed/actual chainmask of the radio.
# USAGE EXAMPLE(S):
#   get_actual_chainmask 15 5GU
###############################################################################
get_actual_chainmask()
{
    local NARGS=2
    [ $# -lt ${NARGS} ] &&
        raise "Requires at least '${NARGS}' input argument(s)" -arg
    chainmask=${1}
    freq_band=${2}

    if [ "${freq_band}" == "5G" ]; then
        actual_chainmask=$((${chainmask} << 4))
        echo "${actual_chainmask}"
    else
        echo "${chainmask}"
    fi
}

####################### UNIT OVERRIDE SECTION - STOP ##########################
