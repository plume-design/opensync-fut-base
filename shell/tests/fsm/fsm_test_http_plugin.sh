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
client_connect_file="tools/client/connect_to_wpa.sh"
client_send_curl_file="tools/client/fsm/make_curl_agent_req.sh"
usage() {
    cat << usage_string
fsm/fsm_test_http_plugin.sh [-h] arguments
Description:
    - Script checks logs for FSM HTTP agent message creation - fsm_send_report
Arguments:
    -h  show this help message
    \$1 (expected_user_agent) : User agent to match logs for : (string)(required)
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
            Configure FSM for HTTP plugin test
                Run: ./fsm/fsm_test_http_plugin.sh <LAN-BRIDGE-IF> <FSM-URL-BLOCK> <FSM-URL-REDIRECT>
    - On Client:
            Configure Client to DUT
                Run: /.${client_connect_file} (see ${client_connect_file} -h)
            Send curl request from Client specifying user_agent
                Run /.${client_send_curl_file} (see ${client_send_curl_file} -h)
    - On DEVICE: Run: ./fsm/fsm_test_http_plugin.sh <EXPECTED_USER_AGENT>
Script usage example:
    ./fsm/fsm_test_http_plugin.sh custom_user_agent
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Associated_Clients
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
expected_user_agent=${1}

client_mac=$(get_ovsdb_entry_value Wifi_Associated_Clients mac)
if [ -z "${client_mac}" ]; then
    raise "FAIL: Could not acquire Client MAC address from Wifi_Associated_Clients, is client connected?" -l "fsm/fsm_test_http_plugin.sh"
fi
# shellcheck disable=SC2060,SC2018,SC2019
client_mac=$(echo "${client_mac}" | tr a-z A-Z)
# Use first MAC from Wifi_Associated_Clients
client_mac="${client_mac%%,*}"
# FSM logs objects in non-constant order, reason for multiple grep-s
fsm_message_regex="$LOGREAD |
 tail -3000 |
 grep fsm_send_report |
 grep locationId |
 grep $(get_location_id) |
 grep nodeId |
 grep $(get_node_id) |
 grep httpRequests |
 grep ${client_mac} |
 grep userAgent |
 grep ${expected_user_agent}"
wait_for_function_response 0 "${fsm_message_regex}" 5 &&
    log "fsm/fsm_test_http_plugin.sh: FSM HTTP plugin UserAgent creation message found in logs - Success" ||
    raise "FAIL: Failed to find FSM HTTP message creation in logs, regex used: ${fsm_message_regex} " -l "fsm/fsm_test_http_plugin.sh" -tc
