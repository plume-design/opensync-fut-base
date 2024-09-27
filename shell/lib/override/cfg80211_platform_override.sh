#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   cfg80211 platform overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/cfg80211_platform_override.sh sourced"

###############################################################################
# DESCRIPTION:
#   Function clears the DNS cache.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   If DNS cache on the device was cleared.
# USAGE EXAMPLE(S):
#   clear_dns_cache
###############################################################################
clear_dns_cache()
{
    log "cfg80211_platform_override:clear_dns_cache - Not clearing DNS cache on the device - not required."
}

###############################################################################
# DESCRIPTION:
#   Function checks if the radio TX chainmask is applied at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  Radio TX Chainmask (int, required)
#   $2  Radio interface name (string, required)
# RETURNS:
#   0   Radio TX Chainmask on system matches expected value.
# USAGE EXAMPLE(S):
#   check_tx_chainmask_at_os_level 5 wifi0
###############################################################################
check_tx_chainmask_at_os_level()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "cfg80211_platform_override:check_tx_chainmask_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    tx_chainmask=$1
    if_name=$2

    log "cfg80211_platform_override:check_tx_chainmask_at_os_level - Checking Radio TX Chainmask for interface '$if_name' at OS - LEVEL2"
    wait_for_function_response 0 "iwpriv $if_name get_txchainsoft | grep -F get_txchainsoft:$tx_chainmask"
    if [ $? = 0 ]; then
        log -deb "cfg80211_platform_override:check_tx_chainmask_at_os_level - Tx Chainmask '$tx_chainmask' is set at OS - LEVEL2 - Success"
    else
        wait_for_function_response 0 "iwpriv $if_name get_txchainmask | grep -F get_txchainmask:$tx_chainmask"
        if [ $? = 0 ]; then
            log -deb "cfg80211_platform_override:check_tx_chainmask_at_os_level - Tx Chainmask '$tx_chainmask' is set at OS - LEVEL2 - Success"
        else
            raise "Tx Chainmask '$tx_chainmask' is not set at OS - LEVEL2" -l "cfg80211_platform_override:check_tx_chainmask_at_os_level" -tc
        fi
    fi

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if vlan interface exists at OS level - LEVEL2.
# INPUT PARAMETER(S):
#   $1  Parent interface name (string, required)
#   $2  VLAN ID (int, required)
# RETURNS:
#   0   vlan interface exists on system.
# USAGE EXAMPLE(S):
#  check_vlan_iface eth0 100
###############################################################################
check_vlan_iface()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "cfg80211_platform_override:check_vlan_iface requires ${NARGS} input argument(s), $# given" -arg
    parent_ifname=$1
    vlan_id=$2

    if_name="$parent_ifname.$vlan_id"
    vlan_file="/proc/net/vlan/${if_name}"

    log "cfg80211_platform_override:check_vlan_iface: Checking for '${vlan_file}' existence - LEVEL2"
    wait_for_function_response 0 "[ -e ${vlan_file} ]" &&
        log "cfg80211_platform_override:check_vlan_iface: LEVEL2 - PID '${vlan_file}' is runinng - Success" ||
        raise "LEVEL2 - PID ${vlan_file} is NOT running" -l "cfg80211_platform_override:check_vlan_iface" -tc

    log "cfg80211_platform_override:check_vlan_iface: Output PID ${vlan_file} info:"
    cat "${vlan_file}"

    log "cfg80211_platform_override:check_vlan_iface: Validating PID VLAN config - vlan_id == ${vlan_id} - LEVEL2"
    wait_for_function_response 0 "cat "${vlan_file}" | grep 'VID: ${vlan_id}'" &&
        log "cfg80211_platform_override:check_vlan_iface: LEVEL2 - VID is set to 100 - Success" ||
        raise "LEVEL2 - VID is not set" -l "cfg80211_platform_override:check_vlan_iface" -tc

    log "cfg80211_platform_override:check_vlan_iface: Check parent device for VLAN - LEVEL2"
    wait_for_function_response 0 "cat "${vlan_file}" | grep 'Device: ${parent_ifname}'" &&
        log "cfg80211_platform_override:check_vlan_iface: LEVEL2 - Device is set to '${parent_ifname}' - Success" ||
        raise "LEVEL2 - Device is not set to '${parent_ifname}'" -l "cfg80211_platform_override:check_vlan_iface" -tc

    return 0
}

####################### cfg80211 PLATFORM OVERRIDE SECTION - STOP #########################


####################### cfg80211 UPGRADE OVERRIDE SECTION - START #########################

###############################################################################
# DESCRIPTION:
#   Function echoes upgrade manager's numerical code of identifier.
#   It translates the identifier's string to its numerical code.
#   Raises exception if identifier not found.
# INPUT PARAMETER(S):
#   $1  upgrade_identifier (string, required)
# RETURNS:
#   Echoes upgrade status code.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   get_um_code UPG_ERR_DL_FW
#   get_um_code UPG_STS_FW_DL_END
###############################################################################
get_um_code()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "cfg80211_platform_override:get_um_code requires ${NARGS} input argument(s), $# given" -arg
    upgrade_identifier=$1

    case "$upgrade_identifier" in
        "UPG_ERR_ARGS")
            echo  "-1"
            ;;
        "UPG_ERR_URL")
            echo  "-3"
            ;;
        "UPG_ERR_DL_FW")
            echo  "-4"
            ;;
        "UPG_ERR_DL_MD5")
            echo  "-5"
            ;;
        "UPG_ERR_MD5_FAIL")
            echo  "-6"
            ;;
        "UPG_ERR_IMG_FAIL")
            echo  "-7"
            ;;
        "UPG_ERR_FL_ERASE")
            echo  "-8"
            ;;
        "UPG_ERR_FL_WRITE")
            echo  "-7"
            ;;
        "UPG_ERR_FL_CHECK")
            echo  "-10"
            ;;
        "UPG_ERR_BC_SET")
            echo  "-11"
            ;;
        "UPG_ERR_APPLY")
            echo  "-12"
            ;;
        "UPG_ERR_BC_ERASE")
            echo  "-14"
            ;;
        "UPG_ERR_SU_RUN ")
            echo  "-15"
            ;;
        "UPG_ERR_DL_NOFREE")
            echo  "-16"
            ;;
        "UPG_STS_FW_DL_START")
            echo  "10"
            ;;
        "UPG_STS_FW_DL_END")
            echo  "11"
            ;;
        "UPG_STS_FW_WR_START")
            echo  "20"
            ;;
        "UPG_STS_FW_WR_END")
            echo  "21"
            ;;
        "UPG_STS_FW_BC_START")
            echo  "30"
            ;;
        "UPG_STS_FW_BC_END")
            echo  "31"
            ;;
        *)
            raise "Unknown upgrade_identifier {given:=$upgrade_identifier}" -l "cfg80211_platform_override:get_um_code" -arg
            ;;
    esac
}

####################### cfg80211 UPGRADE OVERRIDE SECTION - STOP ##########################
