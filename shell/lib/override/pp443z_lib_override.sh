#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   PP443Z libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/pp443z_lib_override.sh sourced"

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
    log -deb "pp443z_lib_override:check_wpa3_compatibility - WPA3 compatible"
    return 0
}

####################### UNIT OVERRIDE SECTION - STOP ##########################
