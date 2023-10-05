#!/bin/sh

####################### INFORMATION SECTION - START ###########################
#
#   Broadcom (BCM) platform overrides
#
####################### INFORMATION SECTION - STOP ############################

echo "${FUT_TOPDIR}/shell/lib/override/bcm_platform_override.sh sourced"

###############################################################################
# DESCRIPTION:
#   Function starts wireless driver on the device.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   0   Wireless driver started on device.
# USAGE EXAMPLE(S):
#   start_wireless_driver
###############################################################################
start_wireless_driver()
{
    log "bcm_platform_override:start_wireless_driver - Starting wireless driver"
    /etc/init.d/bcm-wlan-drivers.sh start ||
        raise "FAIL: Could not start wireless driver" -l "bcm_platform_override:start_wireless_driver" -ds
}

###############################################################################
# DESCRIPTION:
#   Function stops wireless driver on a device.
# INPUT PARAMETER(S):
#   None.
# RETURNS:
#   None.
# USAGE EXAMPLE(S):
#   stop_wireless_driver
###############################################################################
stop_wireless_driver()
{
    /etc/init.d/bcm-wlan-drivers.sh stop
}

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
#   Function empties all VIF interfaces by emptying the Wifi_VIF_Config table.
#   On BCM does not wait for Wifi_VIF_State table to be empty.
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   $1  wait timeout in seconds (int, optional, default=60)
# RETURNS:
#   None.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   vif_clean
#   vif_clean 240
###############################################################################
vif_clean()
{
    VIF_CLEAN_TIMEOUT=${1:-60}

    log -deb "bcm_platform_override:vif_clean - Purging VIF"
    empty_ovsdb_table Wifi_VIF_Config ||
        raise "FAIL: empty_ovsdb_table - Could not empty Wifi_VIF_Config table" -l "bcm_platform_override:vif_clean" -oe
    sleep 5
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
        raise "FAIL: Tx Chainmask '$tx_chainmask' is not set at OS - LEVEL2" -l "bcm_platform_override:check_tx_chainmask_at_os_level" -tc

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
        raise "FAIL: Beacon interval '$bcn_int' for '$vif_if_name' is not set at OS - LEVEL2" -l "bcm_platform_override:check_beacon_interval_at_os_level" -tc

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
        raise "FAIL: LEVEL2 - system file entry '${vlan_file}' does not exist" -l "bcm_platform_override:check_vlan_iface" -tc

    return 0
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
#   Sep 30 09:29:52 WM[2724]: <INFO> MISC: wl0.2: csa completed (52 (0xec32))
###############################################################################
check_sta_send_csa_message()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:check_sta_send_csa_message requires ${NARGS} input argument(s), $# given" -arg
    gw_vif_mac=$1
    gw_csa_channel=$2
    ht_mode=$3

    wm_csa_log_grep="$LOGREAD | grep -i 'csa completed' | grep -i '$gw_csa_channel'"
    wait_for_function_response 0 "${wm_csa_log_grep}" 90 &&
        log "bcm_platform_override:check_sta_send_csa_message : 'csa completed' message found in logs for channel:${gw_csa_channel} with HT mode: ${ht_mode} - Success" ||
        raise "FAIL: Failed to find 'csa completed' message in logs for channel: ${gw_csa_channel} with HT mode: ${ht_mode}" -l "bcm_platform_override:check_sta_send_csa_message" -tc
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

###############################################################################
# DESCRIPTION:
#   Function checks leaf report log messages.
#   Supported radio bands: 2.4G, 5GL, 5GU
#   Supported log types: initializing, parsed, marked_connected
#   Raises exception on fail:
#       - incorrect log type provided
#       - logs not found
# INPUT PARAMETER(S):
#   $1  radio band (string, required)
#   $2  client mac (string, required)
#   $3  log type (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_leaf_report_log 5GL <client MAC> initializing
#   check_leaf_report_log 5GL <client MAC> parsed
###############################################################################
check_leaf_report_log()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:check_leaf_report_log requires ${NARGS} input argument(s), $# given" -arg
    sm_radio_band=$1
    sm_leaf_mac_address=$(echo "$2" | tr a-z A-Z)
    sm_log_type=$3

    case $sm_log_type in
        *initializing*)
            log_msg="Checking logs for 'Initializing $sm_radio_band client reporting'"
            die_msg="Not initializing $sm_radio_band client reporting"
            pass_msg="Initializing $sm_radio_band client reporting"
            sm_log_grep="$LOGREAD | grep -i 'Initializing $sm_radio_band' | grep -i 'client reporting'"
        ;;
        *parsed*)
            log_msg="Checking logs for 'Parsed $sm_radio_band client MAC $sm_leaf_mac_address'"
            die_msg="Not parsed $sm_radio_band client MAC $sm_leaf_mac_address"
            pass_msg="Parsed $sm_radio_band client MAC $sm_leaf_mac_address"
            sm_log_grep="$LOGREAD | grep -i 'Parsed $sm_radio_band client MAC $sm_leaf_mac_address'"
        ;;
        *marked_connected*)
            log_msg="Checking logs for 'Marked $sm_radio_band client $sm_leaf_mac_address connected'"
            die_msg="Not marked $sm_radio_band client $sm_leaf_mac_address connected"
            pass_msg="Marked $sm_radio_band client $sm_leaf_mac_address connected"
            sm_log_grep="$LOGREAD | grep -i 'Marked $sm_radio_band' | grep -i 'client $sm_leaf_mac_address connected'"
        ;;
        *)
            raise "FAIL: Incorrect log type provided" -l "bcm_platform_override:check_leaf_report_log" -arg
        ;;
    esac
    log -deb "bcm_platform_override:check_leaf_report_log - $log_msg"
    wait_for_function_response 0 "${sm_log_grep}" 60 &&
        log -deb "bcm_platform_override:check_leaf_report_log - $pass_msg - Success" ||
        raise "FAIL: $die_msg" -l "bcm_platform_override:check_leaf_report_log" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks existence of leaf report messages.
#   Supported radio bands: 2.4G, 5GL, 5GU
#   Supported report type: raw
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   $1  radio band (string, required)
#   $2  reporting interval (int, required)
#   $3  sampling interval (int, required)
#   $4  report type (string, required)
#   $5  leaf mac (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   inspect_leaf_report 5GL 10 5 raw <leaf MAC>
###############################################################################
inspect_leaf_report()
{
    local NARGS=5
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:inspect_leaf_report requires ${NARGS} input argument(s), $# given" -arg
    sm_radio_band=$1
    sm_reporting_interval=$2
    sm_sampling_interval=$3
    sm_report_type=$4
    sm_leaf_mac=$5

    if [[ -z $sm_leaf_mac ]]; then
        raise "FAIL: Empty leaf MAC address" -l "bcm_platform_override:inspect_leaf_report" -ow
    fi

    empty_ovsdb_table Wifi_Stats_Config ||
        raise "FAIL: Could not empty Wifi_Stats_Config: empty_ovsdb_table" -l "bcm_platform_override:inspect_leaf_report" -oe

    insert_wifi_stats_config \
        "$sm_radio_band" \
        "[\"set\",[]]" \
        "survey" \
        "[\"set\",[]]" \
        "$sm_reporting_interval" \
        "$sm_sampling_interval" \
        "$sm_report_type" &&
            log -deb "bcm_platform_override:inspect_leaf_report - Wifi_Stats_Config inserted - Success" ||
            raise "FAIL: Could not insert Wifi_Stats_Config: insert_wifi_stats_config" -l "bcm_platform_override:inspect_leaf_report" -oe

    insert_wifi_stats_config \
        "$sm_radio_band" \
        "[\"set\",[]]" \
        "client" \
        "[\"set\",[]]" \
        "$sm_reporting_interval" \
        "$sm_sampling_interval" \
        "$sm_report_type" &&
            log -deb "bcm_platform_override:inspect_leaf_report - Wifi_Stats_Config inserted - Success" ||
            raise "FAIL: Could not insert Wifi_Stats_Config: insert_wifi_stats_config" -l "bcm_platform_override:inspect_leaf_report" -oe

    check_leaf_report_log "$sm_radio_band" "$sm_leaf_mac" initializing
    check_leaf_report_log "$sm_radio_band" "$sm_leaf_mac" parsed
    check_leaf_report_log "$sm_radio_band" "$sm_leaf_mac" marked_connected

    log "bcm_platform_override:inspect_leaf_report - Emptying Wifi_Stats_Config table"
    empty_ovsdb_table Wifi_Stats_Config &&
        log -deb "bcm_platform_override:inspect_leaf_report - Wifi_Stats_Config table emptied - Success" ||
        raise "FAIL: Could not empty Wifi_Stats_Config table" -l "bcm_platform_override:inspect_leaf_report" -oe

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function checks existence of survey report log messages.
#   Supported radio bands: 2.4G, 5GL, 5GU
#   Supported survey types: on-chan, off-chan
#   Supported log types: processing_survey, sending_survey_report
#   Raises exception on fail:
#       - incorrect log type provided
#       - logs not found
# INPUT PARAMETER(S):
#   $1  radio band (string, required)
#   $2  channel (int, required)
#   $3  survey type (string, required)
#   $4  log type (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_survey_report_log 5GL 1 on-chan processing_survey
#   check_survey_report_log 5GL 1 on-chan sending_survey_report
###############################################################################
check_survey_report_log()
{
    local NARGS=4
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:check_survey_report_log requires ${NARGS} input argument(s), $# given" -arg
    sm_radio_band=$1
    sm_channel=$2
    sm_survey_type=$3
    sm_log_type=$4

    case $sm_log_type in
        *processing_survey*)
            log_msg="Checking logs for survey $sm_radio_band channel $sm_channel reporting processing survey"
            die_msg="No survey processing done on $sm_radio_band $sm_survey_type on channel $sm_channel"
            pass_msg="Survey processing done on $sm_radio_band $sm_survey_type on channel $sm_channel"
            sm_log_grep="$LOGREAD | tail -500 | grep -i 'Processing $sm_radio_band' | grep -i '$sm_survey_type $sm_channel'"
        ;;
        *sending_survey_report*)
            log_msg="Checking logs for survey $sm_radio_band channel $sm_channel reporting sending survey"
            die_msg="No survey sending done on $sm_radio_band $sm_survey_type on channel $sm_channel"
            pass_msg="Survey sending done on $sm_radio_band $sm_survey_type on channel $sm_channel"
            sm_log_grep="$LOGREAD | tail -500 | grep -i 'Sending $sm_radio_band' | grep -i '$sm_survey_type survey report'"
            ;;
        *)
            raise "FAIL: Incorrect log type provided" -l "bcm_platform_override:check_survey_report_log" -arg
            ;;
    esac
    log "bcm_platform_override:check_survey_report_log - $log_msg"
    wait_for_function_response 0 "${sm_log_grep}" 30 &&
        log -deb "bcm_platform_override:check_survey_report_log - $pass_msg - Success" ||
        raise "FAIL: $die_msg" -l "bcm_platform_override:check_survey_report_log" -tc

    return 0
}

###############################################################################
# DESCRIPTION:
#   Function inspects existence of all survey report messages.
#   Supported radio bands: 2.4G, 5GL, 5GU
#   Supported survey types: on-chan, off-chan
#   Supported report type: raw
#   Raises exception if fails to empty table Wifi_Stats_Config.
# INPUT PARAMETER(S):
#   $1  radio band (string, required)
#   $2  channel (int, required)
#   $3  survey type (string, required)
#   $4  reporting interval (int, required)
#   $5  sampling interval (int, required)
#   $6  report type (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   check_survey_report_log 5GL 1 on-chan 10 5 raw
###############################################################################
inspect_survey_report()
{
    local NARGS=7
    [ $# -ne ${NARGS} ] &&
        raise "bcm_platform_override:inspect_survey_report requires ${NARGS} input argument(s), $# given" -arg
    sm_radio_band=$1
    sm_channel=$2
    sm_survey_type=$3
    sm_reporting_interval=$4
    sm_sampling_interval=$5
    sm_report_type=$6
    sm_survey_interval=$7
    sm_stats_type="survey"

    sm_channel_list="[\"set\",[$sm_channel]]"

    empty_ovsdb_table Wifi_Stats_Config ||
        raise "FAIL: empty_ovsdb_table - Could not empty Wifi_Stats_Config" -l "bcm_platform_override:inspect_survey_report" -oe

    insert_wifi_stats_config \
        "$sm_radio_band" \
        "$sm_channel_list" \
        "$sm_stats_type" \
        "$sm_survey_type" \
        "$sm_reporting_interval" \
        "$sm_sampling_interval" \
        "$sm_report_type" \
        "$sm_survey_interval" &&
            log -deb "bcm_platform_override:inspect_survey_report - Wifi_Stats_Config inserted - Success" ||
            raise "FAIL: Could not insert Wifi_Stats_Config: insert_wifi_stats_config" -l "bcm_platform_override:inspect_survey_report" -oe

    check_survey_report_log "$sm_radio_band" "$sm_channel" "$sm_survey_type" processing_survey
    check_survey_report_log "$sm_radio_band" "$sm_channel" "$sm_survey_type" sending_survey_report

    empty_ovsdb_table Wifi_Stats_Config ||
        raise "FAIL: empty_ovsdb_table - Could not empty Wifi_Stats_Config table" -l "bcm_platform_override:inspect_survey_report" -oe

    return 0
}
