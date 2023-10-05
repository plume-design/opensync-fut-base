#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   MediaTek (MTK) platform overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/mtk_platform_override.sh sourced"

##############################################################################
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
    log -deb "mtk_platform_override:clear_dns_cache - Clearing DNS cache."

    process="dnsmasq"
    $(killall -HUP ${process})
    if [ $? -eq 0 ]; then
        log -deb "mtk_platform_override:clear_dns_cache - ${process} killed - DNS cache cleared - Success"
        return 0
    else
        log -err "FAIL: mtk_platform_override:clear_dns_cache - ${process} kill failed - DNS cache not cleared"
        return 1
    fi
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
        raise "mtk_platform_override:check_vlan_iface requires ${NARGS} input argument(s), $# given" -arg
    parent_ifname=$1
    vlan_id=$2

    if_name="$parent_ifname.$vlan_id"
    vlan_file="/proc/net/vlan/${if_name}"

    log "mtk_platform_override:check_vlan_iface: Checking for '${vlan_file}' existence - LEVEL2"
    wait_for_function_response 0 "[ -e ${vlan_file} ]" &&
        log "mtk_platform_override:check_vlan_iface: LEVEL2 - PID '${vlan_file}' is runinng - Success" ||
        raise "FAIL: LEVEL2 - PID ${vlan_file} is NOT running" -l "mtk_platform_override:check_vlan_iface" -tc

    log "mtk_platform_override:check_vlan_iface: Output PID ${vlan_file} info:"
    cat "${vlan_file}"

    log "mtk_platform_override:check_vlan_iface: Validating PID VLAN config - vlan_id == ${vlan_id} - LEVEL2"
    wait_for_function_response 0 "cat "${vlan_file}" | grep 'VID: ${vlan_id}'" &&
        log "mtk_platform_override:check_vlan_iface: LEVEL2 - VID is set to 100 - Success" ||
        raise "FAIL: LEVEL2 - VID is not set" -l "mtk_platform_override:check_vlan_iface" -tc

    log "mtk_platform_override:check_vlan_iface: Check parent device for VLAN - LEVEL2"
    wait_for_function_response 0 "cat "${vlan_file}" | grep 'Device: ${parent_ifname}'" &&
        log "mtk_platform_override:check_vlan_iface: LEVEL2 - Device is set to '${parent_ifname}' - Success" ||
        raise "FAIL: LEVEL2 - Device is not set to '${parent_ifname}'" -l "mtk_platform_override:check_vlan_iface" -tc

    return 0
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
        raise "mtk_platform_override:check_tx_chainmask_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    tx_chainmask=$(printf "%x" $1)
    if_name=$2

    log "mtk_platform_override:check_tx_chainmask_at_os_level - Checking Radio TX Chainmask for interface '$if_name' at OS - LEVEL2"
    wait_for_function_response 0 "iw $if_name info | grep -F 'Configured Antennas: TX 0x$tx_chainmask'"
    if [ $? = 0 ]; then
        log -deb "mtk_platform_override:check_tx_chainmask_at_os_level - Tx Chainmask '$tx_chainmask' is set at OS - LEVEL2 - Success"
    else
        raise "FAIL: Tx Chainmask '$tx_chainmask' is not set at OS - LEVEL2" -l "mtk_platform_override:check_tx_chainmask_at_os_level" -tc
    fi

    return 0
}
