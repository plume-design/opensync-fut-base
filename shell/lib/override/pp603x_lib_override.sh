#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   PP603X libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/pp603x_lib_override.sh sourced"

####################### UNIT OVERRIDE SECTION - START #########################

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
    log -deb "pp603x_lib_override:check_wpa3_compatibility - WPA3 compatible"
    return 0
}

###############################################################################
# DESCRIPTION:
#   Function returns channel set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
# RETURNS:
#   Echoes channel set for interface
# USAGE EXAMPLE(S):
#   get_channel_from_os home-ap-24
###############################################################################
get_channel_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "pp603x_lib_override:get_channel_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    iw $vif_if_name info | grep -F channel | awk '{ print $2 }'
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
        raise "pp603x_lib_override:get_ht_mode_from_os requires ${NARGS} input argument(s), $# given" -arg
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

    if [ "${freq_band}" = "5G" ] || [ "${freq_band}" = "5g" ]; then
        actual_chainmask=$((${chainmask} << 4))
        echo "${actual_chainmask}"
    else
        echo "${chainmask}"
    fi
}

####################### UNIT OVERRIDE SECTION - STOP ##########################
