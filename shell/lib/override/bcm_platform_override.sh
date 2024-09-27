#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   Broadcom (BCM) platform overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/bcm_platform_override.sh sourced"

###############################################################################
# DESCRIPTION:
#   Function checks if device supports WPA3
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   1   Always.
# USAGE EXAMPLE(S):
#   check_wpa3_compatibility
###############################################################################
check_wpa3_compatibility()
{
    log -deb "bcm_platform_override:check_wpa3_compatibility - WPA3 incompatible"
    return 1
}

###############################################################################
# DESCRIPTION:
#   Function returns Radio TX Power set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
# RETURNS:
#   Echoes Radio TX Power set for interface
# USAGE EXAMPLE(S):
#   get_tx_power_from_os home-ap-24
###############################################################################
get_tx_power_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:get_tx_power_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    wl -i $vif_if_name txpwr | awk '{print $1}' | awk -F '.' '{print $1}'
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
#   check_tx_chainmask_at_os_level 3 wl0
###############################################################################
check_tx_chainmask_at_os_level()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:check_tx_chainmask_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    tx_chainmask=$1
    if_name=$2

    log "bcm_platform_override:check_tx_chainmask_at_os_level - Checking Radio TX Chainmask for interface '$wm2_if_name' at OS - LEVEL2"
    wait_for_function_response 0 "wl -a $if_name txchain | grep -F $tx_chainmask" &&
        log -deb "bcm_platform_override:check_tx_chainmask_at_os_level - Tx Chainmask '$tx_chainmask' is set at OS - LEVEL2 - Success" ||
        raise "Tx Chainmask '$tx_chainmask' is not set at OS - LEVEL2" -l "bcm_platform_override:check_tx_chainmask_at_os_level" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks if Beacon interval is applied at OS - LEVEL2.
#   Function raises an exception if beacon interval is not applied.
# INPUT PARAMETER(S):
#   $1  Beacon interval (int, required)
#   $2  VIF interface name (string, required)
# RETURNS:
#   0   Beacon interval on system matches expected value
# USAGE EXAMPLE(S):
#   check_beacon_interval_at_os_level 600 home-ap-U50
###############################################################################
check_beacon_interval_at_os_level()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:check_beacon_interval_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    bcn_int=$1
    vif_if_name=$2

    log "bcm_platform_override:check_beacon_interval_at_os_level - Checking Beacon interval at OS - LEVEL2"
    wait_for_function_response 0 "wl -a $vif_if_name bi | grep -F $bcn_int" &&
        log -deb "bcm_platform_override:check_beacon_interval_at_os_level - Beacon interval '$bcn_int' for '$vif_if_name' is set at OS - LEVEL2 - Success" ||
        raise "Beacon interval '$bcn_int' for '$vif_if_name' is not set at OS - LEVEL2" -l "bcm_platform_override:check_beacon_interval_at_os_level" -tc

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
#   get_channel_from_os wl0
###############################################################################
get_channel_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:get_channel_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    wl -a $vif_if_name channel | grep -F "current mac channel" | cut -f2
}

###############################################################################
# DESCRIPTION:
#   Function returns HT mode set at OS - LEVEL2.
# INPUT PARAMETER(S):
#   $1  VIF interface name (string, required)
#   $2  channel (int, required)
# RETURNS:
#   Echoes HT mode set for interface
# USAGE EXAMPLE(S):
#   get_ht_mode_from_os wl1.2 1
###############################################################################
get_ht_mode_from_os()
{
    local NARGS=2
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:get_ht_mode_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1
    channel=$2

    chanspec_str=$(wl -a "$vif_if_name" chanspec | cut -d' ' -f1)
    echo $chanspec_str | grep -q "/160"
    if [ $? -eq 0 ]; then
        echo "HT160"
        exit 0
    fi
    echo $chanspec_str | grep -q "/80"
    if [ $? -eq 0 ]; then
        echo "HT80"
        exit 0
    fi
    echo $chanspec_str | grep -q "[lu]"
    if [ $? -eq 0 ]; then
        echo "HT40"
        exit 0
    fi
    echo $chanspec_str | grep -qw "$channel"
    if [ $? -eq 0 ]; then
        echo "HT20"
        exit 0
    fi
    exit 1
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
        raise "bcm_platform_override:check_vlan_iface requires ${NARGS} input argument(s), $# given" -arg
    parent_ifname=$1
    vlan_id=$2

    if_name="$parent_ifname.$vlan_id"
    vlan_file="/sys/class/net/${if_name}"

    log "bcm_platform_override:check_vlan_iface: Checking for ${vlan_file} existence - LEVEL2"
    wait_for_function_response 0 "[ -e ${vlan_file} ]" &&
        log "bcm_platform_override:check_vlan_iface: LEVEL2 - system file entry '${vlan_file}' exists - Success" ||
        raise "LEVEL2 - system file entry '${vlan_file}' does not exist" -l "bcm_platform_override:check_vlan_iface" -tc

    return 0
}

####################### Broadcom (BCM) PLATFORM OVERRIDE SECTION - STOP #########################

###################################################################################
# DESCRIPTION:
#   Function clears the DNS cache on BCM platforms by killing the dnsmasq process.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   On successful DNS cache clear.
#   1   On failure to clear DNS cache.
# USAGE EXAMPLE(S):
#   clear_dns_cache
###############################################################################
clear_dns_cache()
{
    log -deb "bcm_platform_override:clear_dns_cache - Clearing DNS cache."

    process="dnsmasq"
    $(killall -HUP ${process})
    if [ $? -eq 0 ]; then
        log -deb "bcm_platform_override:clear_dns_cache - ${process} killed - DNS cache cleared - Success"
        return 0
    else
        log -err "FAIL: bcm_platform_override:clear_dns_cache - ${process} kill failed - DNS cache not cleared"
        return 1
    fi
}
