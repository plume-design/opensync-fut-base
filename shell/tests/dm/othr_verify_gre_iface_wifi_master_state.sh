#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
othr/othr_verify_gre_iface_wifi_master_state.sh [-h] arguments
Description:
    - Script verifies wifi_master_state table is populated with GRE interface
Arguments:
    -h : show this help message
    \$1 (bhaul_ap_if_name) : used for bhaul ap interface name : (string)(required)
    \$2 (gre_if_name)      : used as GRE interface name       : (string)(required)
    \$3 (gre_mtu)          : used for GRE MTU                 : (string)(required)

    # Configure DUT bhaul-ap
    # On DUT: ./fut-base/shell//tools/device/vif_reset.sh
    # On DUT: ./fut-base/shell//tools/device/create_inet_interface.sh  -if_name br-home -if_type bridge -enabled true -network true -NAT false -ip_assign_scheme dhcp
    # On DUT: ./fut-base/shell//tools/device/create_radio_vif_interface.sh  -if_name wifi0 -vif_if_name bhaul-ap-24 -vif_radio_idx 1 \
        -channel 6 -ht_mode HT40 -hw_mode 11n -enabled true -mac_list '["set",["60:b4:f7:f0:0e:b6"]]'
        -mac_list_type whitelist -mode ap -security '["map",[["encryption","WPA-PSK"],["key","FutTestPSK"],["mode","2"]]]'
        -ssid fut-5515.bhaul -ssid_broadcast disabled
    # On DUT: ./fut-base/shell//tools/device/create_inet_interface.sh  -if_name bhaul-ap-24 -if_type vif -broadcast_n 255 \
        -inet_addr_n 129 -subnet 169.254.6 -netmask 255.255.255.128 -ip_assign_scheme static
        -mtu 1600 -NAT false -enabled true -network true

    # Verify wifi_master_state table contents for GRE interface
    # On DUT: ./fut-base/shell//tests/dm/othr_verify_gre_iface_wifi_master_state.sh  bhaul-ap-24 gre-ifname-100 1562
Script usage example:
    ./othr/othr_verify_gre_iface_wifi_master_state.sh bhaul-ap-50 gre-ifname-100 1562
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Master_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_verify_gre_iface_wifi_master_state.sh" -arg
bhaul_ap_if_name=${1}
gre_name=${2}
gre_mtu=${3}

remote_inet_addr="1.1.1.1"
bhaul_ip_assign_scheme="none"

log "othr/othr_verify_gre_iface_wifi_master_state.sh: - Verify wifi_master_state table is populated with GRE interface"

${OVSH} s Wifi_Master_State
if [ $? -eq 0 ]; then
    log "othr/othr_verify_gre_iface_wifi_master_state.sh: Wifi_Master_State table exists"
else
    raise "Wifi_Master_State table does not exist" -l "othr/othr_verify_gre_iface_wifi_master_state.sh" -tc
fi

ap_inet_addr=$(get_ovsdb_entry_value Wifi_Inet_Config inet_addr -w if_name "${bhaul_ap_if_name}" -r)

# TESTCASE:
log "othr/othr_verify_gre_iface_wifi_master_state.sh: Create GW GRE parent interface"
create_inet_entry \
    -if_name "${gre_name}" \
    -if_type "gre" \
    -gre_ifname "${bhaul_ap_if_name}" \
    -gre_local_inet_addr "${ap_inet_addr// /}" \
    -gre_remote_inet_addr "${remote_inet_addr}" \
    -ip_assign_scheme "${bhaul_ip_assign_scheme}" \
    -mtu "${gre_mtu}" \
    -network true \
    -enabled true &&
        log "othr/othr_verify_gre_iface_wifi_master_state.sh: Interface ${gre_name} created - Success" ||
        raise "Failed to create interface ${gre_name}" -l "othr/othr_verify_gre_iface_wifi_master_state.sh" -ds

check_ovsdb_entry Wifi_Master_State -w if_name ${gre_name} &&
    log "othr/othr_verify_gre_iface_wifi_master_state.sh: Wifi_Master_State populated with GRE interface '${gre_name}' - Success" ||
    raise "Wifi_Master_State not populated with GRE interface '${gre_name}'" -l "othr/othr_verify_gre_iface_wifi_master_state.sh" -tc

pass
