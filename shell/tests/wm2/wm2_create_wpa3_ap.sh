#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"
usage()
{
cat << usage_string
wm2/wm2_create_wpa3_ap.sh [-h] arguments
Description:
    - Script creates AP with WPA3-Personal (SAE) authentication on chosen radio interface.
      Then waits for AP to set up properly by checking Wifi_VIF_State
Arguments:
    -h  show this help message
    \$1  (vif_radio_idx) : Wifi_VIF_Config::vif_radio_idx             : (int)(required)
    \$2  (radio_if_name) : Wifi_Radio_Config::if_name                 : (string)(required)
    \$3  (ssid)          : Wifi_VIF_Config::ssid                      : (string)(required)
    \$4  (ssid_broadcast): Wifi_VIF_Config::ssid_broadcast            : (string)(required)
    \$5  (wpa_psks)      : Wifi_VIF_Config::wpa_psks                  : (string)(required)
    \$6  (wpa_oftags)    : Wifi_VIF_Config::wpa_oftags                : (string)(required)
    \$7  (channel)       : Wifi_Radio_Config::channel                 : (int)(required)
    \$8  (ht_mode)       : Wifi_Radio_Config::ht_mode                 : (string)(required)
    \$9  (hw_mode)       : Wifi_Radio_Config::hw_mode                 : (string)(required)
    \$10 (vif_if_name)   : Wifi_VIF_Config::if_name                   : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_create_wpa3_ap.sh 2 wl1 fut-wpa3-ssid enabled '["map",[["key-0","fut-wpa3-psk"]]]' '["map",[["key-0","home--1"]]]' 1 HT20 11ax wl1.2
Script usage example:
    ./wm2/wm2_create_wpa3_ap.sh 2 wl1 fut-wpa3-ssid enabled '["map",[["key-0","fut-wpa3-psk"]]]' '["map",[["key-0","home--1"]]]' 1 HT20 11ax wl1.2
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=10
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wm2/wm2_create_wpa3_ap.sh" -arg
vif_radio_idx=${1}
radio_if_name=${2}
ssid=${3}
ssid_broadcast=${4}
wpa_psks=${5}
wpa_oftags=${6}
channel=${7}
ht_mode=${8}
hw_mode=${9}
vif_if_name=${10}

trap '
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    print_tables Wifi_VIF_Config Wifi_VIF_State
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "wm2/wm2_create_wpa3_ap.sh: WM2 test - Testing WPA3 AP creation - interface $radio_if_name - channel $channel"

log "wm2/wm2_create_wpa3_ap.sh: Cleaning VIF_Config"
vif_reset

log "wm2/wm2_create_wpa3_ap.sh: Creating VIF interface"
create_radio_vif_interface \
    -if_name "$radio_if_name" \
    -vif_if_name "$vif_if_name" \
    -vif_radio_idx "$vif_radio_idx" \
    -ssid "$ssid" \
    -ssid_broadcast "$ssid_broadcast" \
    -wifi_security_type "wpa" \
    -wpa "true" \
    -wpa_key_mgmt "sae" \
    -wpa_psks "$wpa_psks" \
    -wpa_oftags "$wpa_oftags" \
    -channel "$channel" \
    -hw_mode "$hw_mode" \
    -mode "ap" \
    -enabled "true" \
    -ht_mode "$ht_mode" \
    -channel_mode "manual" &&
        log "wm2/wm2_create_wpa3_ap.sh: create_radio_vif_interface - Interface $radio_if_name created - Success" ||
        raise "FAIL: create_radio_vif_interface - Interface $radio_if_name not created" -l "wm2/wm2_create_wpa3_ap.sh" -tc

pass
