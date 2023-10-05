#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

# Default of_port must be unique between fsm tests for valid testing
of_port_default=10002
usage() {
    cat << usage_string
tools/device/configure_http_plugin.sh [-h] arguments
Description:
    - Script configures interfaces FSM settings for HTTP blocking rules
Arguments:
    -h  show this help message
    \$1 (lan_bridge_if_name)  : Interface name used for LAN bridge        : (string)(required)
    \$2 (fsm_plugin)          : Path to FSM plugin under test             : (string)(required)
    \$3 (mqtt_topic)          : Value of MQTT topic                       : (string)(required)
    \$4 (client_mac)          : Connected client MAC address              : (string)(required)
Script usage example:
    ./tools/device/configure_http_plugin.sh br-home /usr/opensync/lib/libfsm_http.so fsm_mqtt_topic ff:ff:ff:ff:ff
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Associated_Clients Openflow_Config
print_tables Flow_Service_Manager_Config FSM_Policy
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=4
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
lan_bridge_if_name=${1}
fsm_plugin=${2}
mqtt_topic=${3}
client_mac=${4}

tap_http_if="${lan_bridge_if_name}.http"
of_port=$(ovs-vsctl get Interface "${tap_http_if}" ofport)

log_title "tools/device/configure_http_plugin.sh: FSM test - Configure http plugin"

log "tools/device/configure_http_plugin.sh: Cleaning FSM OVSDB Config tables"
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
    -i token "dev_flow_http_out" \
    -i table 0 \
    -i rule 'dl_src=${client_mac},tcp,tcp_dst=80' \
    -i priority 200 \
    -i bridge "${lan_bridge_if_name}" \
    -i action "normal,output:${of_port}" &&
        log "tools/device/configure_http_plugin.sh: Ingress rule inserted - Success" ||
        raise "FAIL: Failed to insert_ovsdb_entry" -l "tools/device/configure_http_plugin.sh" -oe

insert_ovsdb_entry Flow_Service_Manager_Config \
    -i if_name "${tap_http_if}" \
    -i handler "dev_http" \
    -i pkt_capt_filter 'tcp' \
    -i plugin "${fsm_plugin}" \
    -i other_config '["map",[["mqtt_v","'"${mqtt_topic}"'"],["dso_init","http_plugin_init"]]]' &&
        log "tools/device/configure_http_plugin.sh: Flow_Service_Manager_Config entry added - Success" ||
        raise "FAIL: Failed to insert Flow_Service_Manager_Config entry" -l "tools/device/configure_http_plugin.sh" -oe
