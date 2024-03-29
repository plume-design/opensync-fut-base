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
    log -deb "pp603x_lib_override:disable_watchdog - Disabling watchdog"
    ${OPENSYNC_ROOTDIR}/bin/wpd --set-auto
    sleep 1
    # shellcheck disable=SC2034
    PID=$(pidof wpd) || raise "wpd not running" -l "pp603x_lib_override:disable_watchdog" -ds
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
        log -deb "pp603x_lib_override:device_init - Watchdog disabled - Success" ||
        raise "FAIL: device_init - Could not disable watchdog" -l "pp603x_lib_override:device_init" -ds

    stop_managers &&
        log -deb "pp603x_lib_override:device_init - Managers stopped - Success" ||
        raise "FAIL: stop_managers - Could not stop managers" -l "pp603x_lib_override:device_init" -ds

    stop_healthcheck &&
        log -deb "pp603x_lib_override:device_init - Healthcheck stopped - Success" ||
        raise "FAIL: stop_healthcheck - Could not stop healthcheck" -l "pp603x_lib_override:device_init" -ds

    disable_fatal_state_cm &&
        log -deb "pp603x_lib_override:device_init - CM fatal state disabled - Success" ||
        raise "FAIL: disable_fatal_state_cm - Could not disable CM fatal state" -l "pp603x_lib_override:device_init" -ds

    return $?
}

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
#   Function checks for CSA (Channel Switch Announcement) message on the leaf
#   device, sent by the GW upon channel change.
# INPUT PARAMETER(S):
#   $1  MAC address of GW (string, required) - Could be empty string "" since PP603X does not log MAC address
#   $2  CSA channel GW switches to (int, required)
#   $3  HT mode (channel bandwidth) (string, required)
# RETURNS:
#   0   CSA message is found in device logs.
# USAGE EXAMPLE(S):
#   check_sta_send_csa_message 1A:2B:3C:4D:5E:6F 6 HT20
#   check_sta_send_csa_message "" 6 HT20
# EXAMPLE DEVICE LOG:
# Oct 10 00:34:01 kernel[2059]: [16190.751424] wlan: [0:I:ANY] ieee80211_mgmt_sta_send_csa_rx_nl_msg: valid=1 chan=48 width=40 sec=-1 cfreq2=0
###############################################################################
check_sta_send_csa_message()
{
    local NARGS=3
    [ $# -ne ${NARGS} ] &&
        raise "pp603x_lib_override:check_sta_send_csa_message requires ${NARGS} input argument(s), $# given" -arg
    gw_vif_mac=$1
    gw_csa_channel=$2
    ht_mode=$3

    wm_csa_log_grep="$LOGREAD | grep -i 'ieee80211_mgmt_sta_send_csa_rx_nl_msg' | grep -i 'valid=1' | grep -i 'chan=${gw_csa_channel}'"
    wait_for_function_response 0 "${wm_csa_log_grep}" 30 &&
        log "pp603x_lib_override:check_sta_send_csa_message : 'ieee80211_mgmt_sta_send_csa_rx_nl_msg' message found in logs for channel:${gw_csa_channel} - Success" ||
        raise "FAIL: Failed to find 'ieee80211_mgmt_sta_send_csa_rx_nl_msg' message in logs for channel: ${gw_csa_channel} with HT mode: ${ht_mode}" -l "pp603x_lib_override:check_sta_send_csa_message" -tc
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
#   Function checks existence of neighbor report messages.
#   Supported radio bands: 2.4G, 5G, 6G
#   Supported survey types: on-chan, off-chan
#   Supported report type: raw
#   Raises exception on fail.
# INPUT PARAMETER(S):
#   $1  radio band (string, required)
#   $2  channel (int, required)
#   $3  survey type (string, required)
#   $4  reporting interval (int, required)
#   $5  sampling interval (int, required)
#   $6  report type (string, required)
#   $7  neighbor ssid (string, required)
#   $8  neighbor MAC address (string, required)
# RETURNS:
#   0   On success.
#   See DESCRIPTION.
# USAGE EXAMPLE(S):
#   inspect_neighbor_report 5G 1 on-chan 10 5 raw <neighbor SSID> <neighbor MAC>
###############################################################################
inspect_neighbor_report()
{
    local NARGS=8
    [ $# -ne ${NARGS} ] &&
        raise "pp603x_lib_override:inspect_neighbor_report requires ${NARGS} input argument(s), $# given" -arg
    sm_radio_band=$1
    sm_channel=$2
    sm_survey_type=$3
    sm_reporting_interval=$4
    sm_sampling_interval=$5
    sm_report_type=$6
    sm_neighbor_ssid=$7
    # shellcheck disable=SC2018,SC2019
    sm_neighbor_mac=$(echo "$8" | tr a-z A-Z)

    sm_channel_list="[\"set\",[$sm_channel]]"

    empty_ovsdb_table Wifi_Stats_Config ||
        raise "FAIL: Could not empty Wifi_Stats_Config: empty_ovsdb_table" -l "pp603x_lib_override:inspect_neighbor_report" -oe

    insert_wifi_stats_config \
        "$sm_radio_band" \
        "$sm_channel_list" \
        "survey" \
        "$sm_survey_type" \
        "$sm_reporting_interval" \
        "$sm_sampling_interval" \
        "$sm_report_type" &&
            log -deb "pp603x_lib_override:inspect_neighbor_report - Wifi_Stats_Config inserted - Success" ||
            raise "FAIL: Could not insert Wifi_Stats_Config: insert_wifi_stats_config" -l "pp603x_lib_override:inspect_neighbor_report" -oe

    insert_wifi_stats_config \
        "$sm_radio_band" \
        "$sm_channel_list" \
        "neighbor" \
        "$sm_survey_type" \
        "$sm_reporting_interval" \
        "$sm_sampling_interval" \
        "$sm_report_type" &&
            log -deb "pp603x_lib_override:inspect_neighbor_report - Wifi_Stats_Config inserted - Success" ||
            raise "FAIL: Could not insert Wifi_Stats_Config: insert_wifi_stats_config" -l "pp603x_lib_override:inspect_neighbor_report" -oe

    check_neighbor_report_log "$sm_radio_band" "$sm_channel" "$sm_survey_type" adding_neighbor "$sm_neighbor_mac" "$sm_neighbor_ssid"
    check_neighbor_report_log "$sm_radio_band" "$sm_channel" "$sm_survey_type" sending_neighbor "$sm_neighbor_mac" "$sm_neighbor_ssid"

    empty_ovsdb_table Wifi_Stats_Config ||
        raise "FAIL: empty_ovsdb_table - Could not empty Wifi_Stats_Config table" -l "pp603x_lib_override:inspect_neighbor_report" -oe

    return 0
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
