#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

usage()
{
cat << usage_string
tools/device/configure_sta_interface.sh [-h] arguments
Description:
    - Configures STA interface and validates it in Wifi_VIF_State table
Arguments:
    -h  show this help message
    See wm2_lib::configure_sta_interface for more information
Script usage example:
    ./tools/device/configure_sta_interface.sh -if_name bhaul-sta-l50 -ssid fut-2568.bhaul -onboard_type gre -channel 36 -clear_wcc -wait_ip -wifi_security_type legacy -security '["map",[["encryption","WPA-PSK"],["key","FutTestPSK"],["mode","2"]]]'
    ./tools/device/configure_sta_interface.sh -if_name bhaul-sta-l50 -ssid fut-2568.bhaul -onboard_type gre -channel 36 -clear_wcc -wait_ip -wifi_security_type wpa -wpa "true" -wpa_key_mgmt "wpa-psk" -wpa_psks '["map",[["key","FutTestPSK"]]]' -wpa_oftags '["map",[["key","home--1"]]]'
usage_string
}

trap '
fut_ec=$?
fut_info_dump_line
print_tables Wifi_Radio_Config Wifi_Radio_State Wifi_VIF_Config Wifi_VIF_State Wifi_Inet_Config Wifi_Inet_State Wifi_Credential_Config || true
check_restore_ovsdb_server
fut_info_dump_line
exit $fut_ec
' EXIT SIGINT SIGTERM


NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/configure_sta_interface.sh" -arg

log "tools/device/$(basename "$0"): configure_sta_interface - Configuring STA interface"
configure_sta_interface "$@" &&
    log "tools/device/$(basename "$0"): configure_sta_interface - Success" ||
    raise "configure_sta_interface - Failed" -l "tools/device/$(basename "$0")" -tc

exit 0
