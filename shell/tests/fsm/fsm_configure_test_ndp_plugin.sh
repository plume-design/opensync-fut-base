#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="fsm/fsm_setup.sh"
create_rad_vif_if_file="tools/device/create_radio_vif_interface.sh"
create_inet_file="tools/device/create_inet_interface.sh"
add_bridge_port_file="tools/device/add_bridge_port.sh"
configure_lan_bridge_for_wan_connectivity_file="tools/device/configure_lan_bridge_for_wan_connectivity.sh"
# Default of_port must be unique between fsm tests for valid testing
of_port_default=10003
usage() {
    cat << usage_string
fsm/fsm_configure_test_ndp_plugin.sh [-h] arguments
Description:
    - Script configures interfaces FSM settings for NDP blocking rules
    - Requires 'ping6' tool be present on the system
Arguments:
    -h  show this help message
    \$1 (lan_bridge_if_name)  : Interface name used for LAN bridge      : (string)(required)
    \$2 (fsm_plugin)          : Path to FSM plugin under test             : (string)(required)
    \$3 (mqtt_topic)          : Value of MQTT topic                       : (string)(required)
    \$4 (client_mac)          : Connected client MAC address              : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
            Create Radio/VIF interface
                Run: ./${create_rad_vif_if_file} (see ${create_rad_vif_if_file} -h)
            Create Inet entry for VIF interface
                Run: ./${create_inet_file} (see ${create_inet_file} -h)
            Create Inet entry for home bridge interface (br-home)
                Run: ./${create_inet_file} (see ${create_inet_file} -h)
            Add bridge port to VIF interface onto home bridge
                Run: ./${add_bridge_port_file} (see ${add_bridge_port_file} -h)
            Configure WAN bridge settings
                Run: ./${configure_lan_bridge_for_wan_connectivity_file} (see ${configure_lan_bridge_for_wan_connectivity_file} -h)
            Update Inet entry for home bridge interface for dhcpd (br-home)
                Run: ./${create_inet_file} (see ${create_inet_file} -h)
            Test FSM for NDP plugin test
                Run: ./fsm/fsm_configure_test_ndp_plugin.sh <LAN-BRIDGE-IF> <FSM-PLUGIN> <MQTT-TOPIC> <CLIENT-MAC>
Script usage example:
    ./fsm/fsm_configure_test_ndp_plugin.sh br-home /usr/opensync/lib/libfsm_ndp.so fsm_mqtt_topic ff:ff:ff:ff:ff
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Associated_Clients
print_tables Openflow_Config Openflow_State
print_tables Flow_Service_Manager_Config FSM_Policy
print_tables IPv6_Neighbors
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=4
[ $# -lt ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
lan_bridge_if_name=${1}
fsm_plugin=${2}
mqtt_topic=${3}
client_mac=${4}

tap_ndp_if="${lan_bridge_if_name}.ndp"
of_port=$(ovs-vsctl get Interface "${tap_ndp_if}" ofport)

log_title "fsm/fsm_configure_test_ndp_plugin.sh: FSM test - Configure ndp plugin"

log "fsm/fsm_configure_test_ndp_plugin.sh: Cleaning FSM OVSDB Config tables"
empty_ovsdb_table Openflow_Config
empty_ovsdb_table Flow_Service_Manager_Config
empty_ovsdb_table FSM_Policy
empty_ovsdb_table Openflow_Tag

log "tools/device/configure_http_plugin.sh: Adding tags to Openflow_Tag"
insert_ovsdb_entry Openflow_Tag \
    -i name "client_mac" \
    -i cloud_value '["set",["'${client_mac}'"]]'

# Insert egress rule to Openflow_Config
insert_ovsdb_entry Openflow_Config \
    -i token "dev_flow_ndp_out" \
    -i table 0 \
    -i rule 'dl_dst=${client_mac},ipv6,nw_proto=58' \
    -i priority 200 \
    -i bridge "${lan_bridge_if_name}" \
    -i action "normal,output:${of_port}" &&
        log "fsm/fsm_configure_test_ndp_plugin.sh: Egress rule inserted - Success" ||
        raise "FAIL: Failed to insert_ovsdb_entry" -l "fsm/fsm_configure_test_ndp_plugin.sh" -oe

# Insert ingress rule to Openflow_Config
insert_ovsdb_entry Openflow_Config \
    -i token "dev_flow_ndp_in" \
    -i table 0 \
    -i rule 'dl_src=${client_mac},ipv6,nw_proto=58' \
    -i priority 200 \
    -i bridge "${lan_bridge_if_name}" \
    -i action "normal,output:${of_port}" &&
        log "fsm/fsm_configure_test_ndp_plugin.sh: Ingress rule inserted - Success" ||
        raise "FAIL: Failed to insert_ovsdb_entry" -l "fsm/fsm_configure_test_ndp_plugin.sh" -oe

insert_ovsdb_entry Flow_Service_Manager_Config \
    -i if_name "${tap_ndp_if}" \
    -i handler "dev_ndp" \
    -i plugin "${fsm_plugin}" \
    -i other_config '["map",[["mqtt_v","'"${mqtt_topic}"'"],["dso_init","ndp_plugin_init"]]]' &&
        log "fsm/fsm_configure_test_ndp_plugin.sh: Flow_Service_Manager_Config entry added - Success" ||
        raise "FAIL: Failed to insert Flow_Service_Manager_Config entry" -l "fsm/fsm_configure_test_ndp_plugin.sh" -oe

log "fsm/fsm_configure_test_ndp_plugin.sh: ping6 clients"
wait_for_function_response 0 "ping6 -c2 -I ${tap_ndp_if} ff02::1" 5 &&
    log "fsm/fsm_configure_test_ndp_plugin.sh: ping6 clients - Success" ||
    log -wrn "fsm/fsm_configure_test_ndp_plugin.sh: Failed to ping6 clients"

wait_for_function_response 0 "${OVSH} s IPv6_Neighbors hwaddr | grep '${client_mac}'" 30 &&
    log "fsm/fsm_configure_test_ndp_plugin.sh: Client added into IPv6_Neighbors table - Success" ||
    raise "FAIL: Client not added into IPv6_Neighbors table" -l "fsm/fsm_configure_test_ndp_plugin.sh" -oe

print_tables IPv6_Neighbors

pass
