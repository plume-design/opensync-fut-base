#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   PP203X libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/pp203x_lib_override.sh sourced"

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
