#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   MR8300-EXT libraries overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/mr8300_ext_lib_override.sh sourced"

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
       raise "mr8300_ext_lib_override:get_tx_power_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    iw $vif_if_name info | grep txpower | awk -F '.' '{print $1}'| awk -F ' ' '{print $2}'
}

###############################################################################
# DESCRIPTION:
#   Function starts wireless driver on the device.
# INPUT PARAMETER(S):
#   None.
# USAGE EXAMPLE(S):
#   start_wireless_driver
###############################################################################
start_wireless_driver()
{
    log "mr8300_ext_lib_override:start_wireless_driver - Starting wireless driver"
    /etc/init.d/wpad restart ||
        raise "FAIL: Could not start wireless driver" -l "mr8300_ext_lib_override:start_wireless_driver" -ds
    sleep 2
}

###############################################################################
# DESCRIPTION:
#   Function checks if Beacon interval is applied at OS - LEVEL2.
#   Function raises an exception if beacon interval is not applied.
# OVERRIDE:
#   This device reports beacon intervals for radios, not VIFs
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
        raise "mr8300_ext_lib_override:check_beacon_interval_at_os_level requires ${NARGS} input argument(s), $# given" -arg
    bcn_int=$1
    vif_if_name=$2

    # Get radio interface from VIF interface
    case "$vif_if_name" in
        "home-ap-24")
            if_name=phy1
        ;;
        "home-ap-l50")
            if_name=phy2
        ;;
        "home-ap-u50")
            if_name=phy0
        ;;
        *)
            raise "FAIL: Incorrect home-ap provided" -l "mr8300_ext_lib_override:check_beacon_interval_at_os_level" -arg
        ;;
    esac

    sleep 10
    beacon_interval=0

    log "mr8300_ext_lib_override:check_beacon_interval_at_os_level - Checking Beacon interval at OS - LEVEL2"
    beacon_interval=$(hostapd_cli -p /var/run/hostapd-${if_name} -i $vif_if_name status | grep beacon_int | awk -F '=' '{print $2}')
    [ $beacon_interval -eq $bcn_int ] &&
        log -deb "mr8300_ext_lib_override:check_beacon_interval_at_os_level - Beacon interval '$bcn_int' for '$vif_if_name' is set at OS - LEVEL2 - Success" ||
        raise "FAIL: Beacon interval '$bcn_int' for '$vif_if_name' is not set at OS - LEVEL2" -l "mr8300_ext_lib_override:check_beacon_interval_at_os_level" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function initializes device for use in FUT.
#   Instead of performing "stop_managers", it only does "stop_openswitch", to
#   avoid removal of certificates in /var/run/openvswitch/
#   It calls a function that instructs CM to prevent the device from rebooting.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   device_init
###############################################################################
device_init()
{
    # 'stop_managers' is removed, because the certificates are deleted in
    # /var/run/openvswitch/ in combination with managers script
    # stop_managers

    stop_openswitch &&
        log -deb "mr8300_ext_lib_override:device_init - stopped OpenvSwitch - Success" ||
        raise "FAIL: Could not stop OpenvSwitch: stop_openswitch" -l "mr8300_ext_lib_override:device_init" -ds
    disable_fatal_state_cm &&
        log -deb "mr8300_ext_lib_override:device_init - CM fatal state disabled - Success" ||
        raise "FAIL: Could not disable CM fatal state" -l "mr8300_ext_lib_override:device_init" -ds
    return $?
}

###############################################################################
# DESCRIPTION:
#   Function re-starts all OpenSync managers.
#   Executes managers script with restart option.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   Last exit status.
# USAGE EXAMPLE(S):
#   restart_managers
###############################################################################
restart_managers()
{
    log -deb "mr8300_ext_lib_override:restart_managers - Restarting OpenSync managers"
    ret=$(/usr/opensync/bin/restart.sh)
    ec=$?
    if [ $ec == 0 ]; then
        log -deb "mr8300_ext_lib_override:restart_managers - Success"
    else
        log -err "mr8300_ext_lib_override:restart_managers - Failure - manager restart exit code ${ec}"
    fi
    return $ec
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
        raise "mr8300_ext_lib_override:get_ht_mode_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1
    channel=$2
    local ht_mode_val=0

    ht_mode_val=$(iw $vif_if_name info | grep  channel | (awk -F ':' '{print $2}'| awk -F 'M' '{print $1}') | tr -d ' ')
    echo "HT$ht_mode_val"
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
        raise "mr8300_ext_lib_override:get_channel_from_os requires ${NARGS} input argument(s), $# given" -arg
    vif_if_name=$1

    iw $vif_if_name info | grep  channel | awk -F ',' '{print $1}' | awk -F ' ' '{print $2}'
}

###############################################################################
# DESCRIPTION:
#  Function returns interface MAC address at OS - LEVEL2.
# INPUT PARAMETER(S):
#  $1  Radio interface name (string, required)
# RETURNS:
#  Echoes MAC address for interface
# USAGE EXAMPLE(S):
#   get_mac_from_os phy0
###############################################################################
get_mac_from_os()
{
    local NARGS=1
    [ $# -ne ${NARGS} ] &&
        raise "mr8300_ext_lib_override:get_mac_from_os requires ${NARGS} input argument(s), $# given" -arg
    if_name=$1

    mac_address=$(cat /sys/class/ieee80211/${if_name}/macaddress)
    echo "$mac_address"
}

###############################################################################
# DESCRIPTION:
#   Function checks for CSA (Channel Switch Announcement) message on the leaf
#   device, sent by the GW upon channel change.
# INPUT PARAMETER(S):
#   $1  MAC address of GW (string, required)
#   $2  CSA channel GW switches to (int, required)
#   $3  HT mode (channel bandwidth) (string, required)
# RETURNS:
#   0   CSA message is found in device logs.
# USAGE EXAMPLE(S):
#   check_sta_send_csa_message 1A:2B:3C:4D:5E:6F 6 HT20
# EXAMPLE DEVICE LOG:
#   Tue Jan 19 14:01:07 2021 daemon.notice wpa_supplicant[4900]: bhaul-sta-24: CTRL-EVENT-STARTED-CHANNEL-SWITCH freq=2437 ht_enabled=1 ch_offset=0 ch_width=20 MHz cf1=2437 cf2=0
###############################################################################
check_sta_send_csa_message()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "mr8300_ext_lib_override:check_sta_send_csa_message requires ${NARGS} input argument(s), $# given" -arg
    gw_vif_mac=$1
    gw_csa_channel=$2
    ht_mode=$3

    wm_csa_log_grep="$LOGREAD | grep -i 'wpa_supplicant' | grep -i 'CTRL-EVENT-STARTED-CHANNEL-SWITCH'"
    wait_for_function_response 0 "${wm_csa_log_grep}" 30 &&
        log "mr8300_ext_lib_override:check_sta_send_csa_message : 'csa completed' message found in logs for channel:${gw_csa_channel} with HT mode: ${ht_mode} - Success" ||
        raise "FAIL: Failed to find 'csa completed' message in logs for channel: ${gw_csa_channel} with HT mode: ${ht_mode}" -l "mr8300_ext_lib_override:check_sta_send_csa_message" -tc
    return 0
}
