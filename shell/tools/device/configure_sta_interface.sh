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
tools/device/configure_sta_interface [-h] arguments
Description:
    - The script configures an STA interface by populating the Wifi_VIF_Config OVSDB table.
    - If the clear_wcc parameter is set to 'true', the Wifi_Credential_Config OVSDB table is cleared.

Arguments:
    -h : show this help message
    (mac_list)               : Wifi_VIF_Config::mac_list                          : (set)(optional)
    (mac_list_type)          : Wifi_VIF_Config::mac_list_type                     : (str)(optional)
    (mode)                   : Wifi_VIF_Config::mode                              : (str)(required)
    (multi_ap)               : Wifi_VIF_Config::multi_ap                          : (str)(optional)
    (parent)                 : Wifi_VIF_State::parent                             : (str)(optional)
    (ssid)                   : Wifi_VIF_Config::ssid                              : (str)(required)
    (vif_if_name)            : Wifi_VIF_Config::if_name                           : (str)(required)
    (wpa)                    : Wifi_VIF_Config::wpa                               : (bool)(required)
    (wpa_key_mgmt)           : Wifi_VIF_Config::wpa_key_mgmt                      : (str)(required)
    (wpa_oftags)             : Wifi_VIF_Config::wpa_oftags                        : (map)(required)
    (wpa_psks)               : Wifi_VIF_Config::wpa_psks                          : (map)(required)
    (clear_wcc)              : clear the Wifi_Credential_Config OVSDB table       : (bool)(optional)
    (wait_ip)                : wait for the STA interface to obtain an IP address : (bool)(optional)

Script usage example:
    ./tools/device/configure_sta_interface.sh -vif_if_name "bhaul-sta-24" -mode "sta" \
    -ssid "86382dfcecc79d9657b8a82cb15fe839" -wpa_oftags '["map",[["key--1","home--1"]]]' -wpa true \
    -wpa_psks '["map",[["key--1","62e2dacd685b91ea8ad2b8df1b592b42"]]]' -wpa_key_mgmt "wpa2-psk"
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State Wifi_VIF_Config Wifi_VIF_State Wifi_Inet_Config Wifi_Inet_State Wifi_Credential_Config || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=6
[ $# -eq ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/device/configure_sta_interface.sh" -arg

log "tools/device/configure_sta_interface.sh: Configure STA interface"

# Pass all arguments to the configure_sta_interface shell function
configure_sta_interface "$@" &&
    log "tools/device/configure_sta_interface.sh: STA interface configured - Success" ||
    raise "STA interface not configured" -l "tools/device/configure_sta_interface.sh" -tc

exit 0
