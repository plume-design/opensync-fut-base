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
tools/device/configure_ap_interface [-h] arguments
Description:
    - The script configures an AP interface by populating the Wifi_Radio_Config and Wifi_VIF_Config OVSDB tables.
    - Optionally:
        - the related Wifi_Inet_Config is also populated, if the perform_network_config argument is set to true
        - the AP interface is added to the bridge, if the bridge argument is provided
Arguments:
    -h : show this help message
    (channel)                : Wifi_Radio_Config::channel             : (int)(required)
    (channel_mode)           : Wifi_Radio_Config::channel_mode        : (str)(required)
    (ht_mode)                : Wifi_Radio_Config::ht_mode             : (str)(required)
    (radio_if_name)          : Wifi_Radio_Config::if_name             : (str)(required)
    (ap_bridge)              : Wifi_VIF_Config::ap_bridge             : (bool)(required)
    (bridge)                 : Wifi_VIF_Config::bridge                : (str)(required)
    (enabled)                : Wifi_VIF_Config::enable                : (bool)(required)
    (mac_list)               : Wifi_VIF_Config::mac_list              : (set)(optional)
    (mac_list_type)          : Wifi_VIF_Config::mac_list_type         : (str)(optional)
    (mode)                   : Wifi_VIF_Config::mode                  : (str)(required)
    (multi_ap)               : Wifi_VIF_Config::multi_ap              : (str)(optional)
    (ssid)                   : Wifi_VIF_Config::ssid                  : (str)(required)
    (ssid_broadcast)         : Wifi_VIF_Config::ssid_broadcast        : (str)(required)
    (vif_if_name)            : Wifi_VIF_Config::if_name               : (str)(required)
    (vif_radio_idx)          : Wifi_VIF_Config::vif_radio_idx         : (int)(required)
    (wpa)                    : Wifi_VIF_Config::wpa                   : (str)(required)
    (wpa_key_mgmt)           : Wifi_VIF_Config::wpa_key_mgmt          : (str)(required)
    (wpa_oftags)             : Wifi_VIF_Config::wpa_oftags            : (map)(required)
    (wpa_psks)               : Wifi_VIF_Config::wpa_psks              : (map)(required)
    (broadcast)              : Wifi_Inet_Config::broadcast            : (str)(optional)
    (dhcpd)                  : Wifi_Inet_Config::dhcpd                : (str)(optional)
    (if_type)                : Wifi_Inet_Config::if_type              : (str)(optional)
    (inet_addr)              : Wifi_Inet_Config::inet_addr            : (bool)(optional)
    (inet_enabled)           : Wifi_Inet_Config::inet_enabled         : (bool)(optional)
    (ip_assign_scheme)       : Wifi_Inet_Config::ip_assign_scheme     : (str)(optional)
    (mtu)                    : Wifi_Inet_Config::mtu                  : (str)(required)
    (NAT)                    : Wifi_Inet_Config::NAT                  : (bool)(optional)
    (netmask)                : Wifi_Inet_Config::NAT                  : (str)(optional)
    (network)                : Wifi_Inet_Config::network              : (bool)(optional)
    (network_if_name)        : Wifi_Inet_Config::if_name              : (str)(optional)
    (perform_network_config) : perform the network configuration      : (bool)(optional)
    (perform_cac)            : perform the channel availability check : (bool)(optional)
Script usage example:
    ./tools/device/configure_ap_interface.sh -channel 6 -channel_mode "manual" -radio_if_name "wifi1" -ht_mode "HT40" \
    -ap_bridge false -bridge "br-home" -enabled true -mac_list '["set",[]]' -mac_list_type "none" -mode "ap" \
    -perform_cac false -ssid_broadcast "enabled" -vif_if_name "home-ap-24" -vif_radio_idx 2 \
    -ssid "86382dfcecc79d9657b8a82cb15fe839" -wpa true -wpa_oftags '["map",[["key--1","home--1"]]]' \
    -wpa_psks '["map",[["key--1","62e2dacd685b91ea8ad2b8df1b592b42"]]]' -wpa_key_mgmt "wpa2-psk" -if_type "vif" \
    -inet_enabled true -ip_assign_scheme "none" -mtu 1600 -NAT false -network true -network_if_name "home-ap-24" \
    -perform_network_config true
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State Wifi_VIF_Config Wifi_VIF_State Wifi_Inet_Config Wifi_Inet_State || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM


NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/configure_ap_interface" -arg

log "tools/device/configure_ap_interface.sh: Configure AP interface"

# Parse the arguments that were passed to the script
while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -channel | \
        -channel_mode | \
        -ht_mode | \
        -radio_if_name | \
        -ap_bridge | \
        -bridge | \
        -enabled | \
        -mac_list | \
        -mac_list_type | \
        -mode | \
        -multi_ap | \
        -ssid | \
        -ssid_broadcast | \
        -vif_radio_idx | \
        -wpa | \
        -wpa_key_mgmt | \
        -wpa_oftags | \
        -wpa_psks)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        -broadcast | \
        -dhcpd | \
        -if_type | \
        -inet_addr | \
        -inet_enabled | \
        -ip_assign_scheme | \
        -mtu | \
        -NAT | \
        -netmask | \
        -network)
            network_args="${network_args} -${option#?} ${1}"
            shift
            ;;
        -vif_if_name)
            radio_vif_args="${radio_vif_args} -vif_if_name ${1}"
            vif_if_name=${1}
            shift
            ;;
        -network_if_name)
            network_args="${network_args} -network_if_name ${1}"
            network_if_name=${1}
            shift
            ;;
        -perform_network_config)
            perform_network_config=${1}
            shift
            ;;
        -perform_cac)
            radio_vif_args="${radio_vif_args} -${option#?} ${1}"
            shift
            ;;
        *)
            raise "Wrong option provided: $option" -l "tools/device/configure_ap_interface.sh" -arg
            ;;
    esac
done
create_radio_vif_interface ${radio_vif_args} &&
    log -deb "tools/device/configure_ap_interface.sh: AP interface created - Success" ||
    raise "AP interface not created" -l "tools/device/configure_ap_interface.sh" -tc

# Create Wifi_Inet_Config entry if the network arguments were provided
if [ "$perform_network_config" = "true" ]; then
    create_inet_entry ${network_args} &&
        log -deb "tools/device/configure_ap_interface.sh: Inet interface ${network_if_name} created - Success" ||
        raise "Inet interface ${network_if_name} not created" -l "tools/device/configure_ap_interface.sh" -tc
fi

# Add AP to bridge if the bridge argument was provided
if [ "$bridge" ]; then
    add_port_to_bridge "${bridge}" "${vif_if_name}" &&
        log -deb "tools/device/configure_ap_interface.sh: Interface ${vif_if_name} added to bridge ${bridge} - Success" ||
        raise "Failed to add interface ${vif_if_name} to bridge ${bridge}" -l "tools/device/configure_ap_interface.sh" -tc
fi
exit 0
