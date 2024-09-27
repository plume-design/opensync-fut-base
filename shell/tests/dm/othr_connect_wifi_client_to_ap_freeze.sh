#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

freeze_src_token="device_freeze_src"
freeze_dst_token="device_freeze_dst"

usage() {
cat <<usage_string
othr/othr_connect_wifi_client_to_ap_freeze.sh [-h] arguments
Description:
    - Script adds Openflow rules to freeze the client.
    - The client freeze procedure differs based on the
      device bridge type (Linux Native Bridge/OVS Bridge)
Arguments:
    -h  show this help message
    \$1  (client_mac)   : MAC address of client connected to ap : (string)(required)
    \$2  (lan_bridge)   : Interface name of LAN bridge          : (string)(required)
Script usage example:
    ./othr/othr_connect_wifi_client_to_ap_freeze.sh a1:b2:c3:d4:e5:f6 br-home
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Openflow_Tag Openflow_Config
    linux_native_bridge_enabled && ebtables -L || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument" -arg
client_mac=${1}
lan_bridge=${2}

log_title "othr/othr_connect_wifi_client_to_ap_freeze.sh: OTHR test - Adding Openflow rules to tables to freeze client"

nb_device_freeze()
{
    # ebtables rules for the INPUT system chain
    insert_ovsdb_entry Netfilter \
        -i name "nfm.filter_input_eth" \
        -i protocol "eth" \
        -i chain "INPUT" \
        -i priority 500 \
        -i rule "" \
        -i status "enabled" \
        -i target "NFM_INPUT" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.input_access_control" \
        -i protocol "eth" \
        -i chain "NFM_INPUT" \
        -i priority 50 \
        -i rule "" \
        -i status "enabled" \
        -i target "ACCESS_CONTROL" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    # ebtables rules for the FORWARD system chain
    insert_ovsdb_entry Netfilter \
        -i name "nfm.filter_forward_eth" \
        -i protocol "eth" \
        -i chain "FORWARD" \
        -i priority 500 \
        -i rule "" \
        -i status "enabled" \
        -i target "NFM_FORWARD" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.forward_access_control" \
        -i protocol "eth" \
        -i chain "NFM_FORWARD" \
        -i priority 50 \
        -i rule "" \
        -i status "enabled" \
        -i target "ACCESS_CONTROL" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    # ebtables rules for the OUTPUT system chain
    insert_ovsdb_entry Netfilter \
        -i name "nfm.filter_output_eth" \
        -i protocol "eth" \
        -i chain "OUTPUT" \
        -i priority 500 \
        -i rule "" \
        -i status "enabled" \
        -i target "NFM_OUTPUT" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.output_access_control" \
        -i protocol "eth" \
        -i chain "NFM_OUTPUT" \
        -i priority 50 \
        -i rule "" \
        -i status "enabled" \
        -i target "ACCESS_CONTROL" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    # ebtables rules for the ACCESS_CONTROL user-defined chain
    insert_ovsdb_entry Netfilter \
        -i name "ac.main_conn" \
        -i protocol "eth" \
        -i chain "ACCESS_CONTROL" \
        -i priority 20 \
        -i rule "" \
        -i status "enabled" \
        -i target "CONNECTION" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    # ebtables rules for the CONNECTION user-defined chain
    insert_ovsdb_entry Netfilter \
        -i chain "CONNECTION" \
        -i enable true \
        -i name "ac.conn_frozen_src" \
        -i priority 30 \
        -i protocol "eth" \
        -i rule '-s ${frozen}' \
        -i status "enabled" \
        -i table "filter" \
        -i target "DROP" ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i chain "CONNECTION" \
        -i enable true \
        -i name "ac.conn_frozen_dst" \
        -i priority 30 \
        -i protocol "eth" \
        -i rule '-d ${frozen}' \
        -i status "enabled" \
        -i table "filter" \
        -i target "DROP" ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    # general ebtables rules
    insert_ovsdb_entry Netfilter \
        -i name "ac.input_return" \
        -i protocol "eth" \
        -i chain "NFM_INPUT" \
        -i priority 100 \
        -i rule "" \
        -i status "enabled" \
        -i target "RETURN" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.forward_return" \
        -i protocol "eth" \
        -i chain "NFM_FORWARD" \
        -i priority 100 \
        -i rule "" \
        -i status "enabled" \
        -i target "RETURN" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.output_return" \
        -i protocol "eth" \
        -i chain "NFM_OUTPUT" \
        -i priority 100 \
        -i rule "" \
        -i status "enabled" \
        -i target "RETURN" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.access_control_return" \
        -i protocol "eth" \
        -i chain "ACCESS_CONTROL" \
        -i priority 100 \
        -i rule "" \
        -i status "enabled" \
        -i target "RETURN" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    insert_ovsdb_entry Netfilter \
        -i name "ac.connection_return" \
        -i protocol "eth" \
        -i chain "CONNECTION" \
        -i priority 100 \
        -i rule "" \
        -i status "enabled" \
        -i target "RETURN" \
        -i table "filter" \
        -i enable true ||
            raise "Could not insert entry to Netfilter table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc
}

ovs_device_freeze()
{
    ${OVSH} i Openflow_Config action:=drop bridge:="${lan_bridge}" priority:=200 rule:='dl_src=${frozen}' table:=0 token:=${freeze_src_token} &&
        log "othr/othr_connect_wifi_client_to_ap_freeze.sh: Entry inserted to Openflow_Config for action 'drop' for dl_src rule - Success" ||
        raise "Failed to insert to Openflow_Config for action 'drop' for dl_src rule" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

    ${OVSH} i Openflow_Config  action:=drop bridge:="${lan_bridge}" priority:=200 rule:='dl_dst=${frozen}' table:=0 token:=${freeze_dst_token} &&
        log "othr/othr_connect_wifi_client_to_ap_freeze.sh: Entry inserted to Openflow_Config for action 'drop' for dl_dst rule - Success" ||
        raise "Failed to insert to Openflow_Config for action 'drop' for dl_dst rule" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc
}

if linux_native_bridge_enabled; then
    nb_device_freeze
else
    ovs_device_freeze
fi

log "othr/othr_connect_wifi_client_to_ap_freeze.sh: Inserting rules into Openflow tables to freeze the client: $client_mac"
${OVSH} i Openflow_Tag name:=frozen cloud_value:="${client_mac}" &&
    log "othr/othr_connect_wifi_client_to_ap_freeze.sh: Entry inserted to Openflow_Tag for name 'frozen', client MAC '$client_mac' - Success" ||
    raise "Failed to add Openflow rules for client $client_mac to Openflow_Tag table" -l "othr/othr_connect_wifi_client_to_ap_freeze.sh" -fc

pass
