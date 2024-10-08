#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

# Fallback to the "/home/plume/" directory in case of missing file
if [ ! -e "$client_upnp_server_file" ]; then
    client_upnp_server_file="/home/plume/upnp/upnp_server.py"
fi

usage() {
    cat << usage_string
fsm/fsm_test_upnp_plugin.sh [-h] arguments
Description:
    - Script checks logs for FSM UPnP message creation - fsm_send_report
Arguments:
    -h  show this help message
    \$1 (deviceType)       : UPnP Device deviceType value       : (string)(required)
    \$2 (friendlyName)     : UPnP Device friendlyName value     : (string)(required)
    \$3 (manufacturer)     : UPnP Device manufacturer value     : (string)(required)
    \$4 (manufacturerURL)  : UPnP Device manufacturerURL value  : (string)(required)
    \$5 (modelDescription) : UPnP Device modelDescription value : (string)(required)
    \$6 (modelName)        : UPnP Device modelName value        : (string)(required)
    \$7 (modelNumber)      : UPnP Device modelNumber value      : (string)(required)
Script usage example:
    ./fsm/fsm_test_upnp_plugin.sh 'urn:fut-test:device:test:1' 'FUT test device' 'FUT testing, Inc' 'https://www.fut.com' 'FUT UPnP service' 'FUT tester' '1.0'
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Associated_Clients
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=7
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
deviceType=${1}
friendlyName=${2}
manufacturer=${3}
manufacturerURL=${4}
modelDescription=${5}
modelName=${6}
modelNumber=${7}

log_title "fsm/fsm_test_upnp_plugin.sh: FSM test - Test UPnP plugin - Verify presence of load message"

client_mac=$(get_ovsdb_entry_value Wifi_Associated_Clients mac)
if [ -z "${client_mac}" ]; then
    raise "Could not acquire Client MAC address from Wifi_Associated_Clients, is client connected?" -l "fsm/fsm_test_upnp_plugin.sh"
fi
# shellcheck disable=SC2018,SC2019
client_mac=$(echo "${client_mac}" | tr a-z A-Z)
# Use first MAC from Wifi_Associated_Clients
client_mac="${client_mac%%,*}"

# FSM logs objects in non-constant order, reason for multiple grep-s
fsm_message_regex="$LOGREAD |
 tail -3000 |
 grep fsm_send_report |
 grep upnpInfo |
 grep deviceType |
 grep '${deviceType}' |
 grep friendlyName |
 grep '${friendlyName}' |
 grep manufacturer |
 grep '${manufacturer}' |
 grep manufacturerURL |
 grep '${manufacturerURL}' |
 grep modelDescription |
 grep '${modelDescription}' |
 grep modelName |
 grep '${modelName}' |
 grep modelNumber |
 grep '${modelNumber}' |
 grep deviceMac |
 grep '${client_mac}' |
 grep locationId |
 grep $(get_location_id) |
 grep nodeId |
 grep $(get_node_id)"
wait_for_function_response 0 "${fsm_message_regex}" 10 &&
    log "fsm/fsm_test_upnp_plugin.sh: FSM UPnP plugin creation message found in logs - Success" ||
    raise "Failed to find FSM UPnP message creation in logs, regex used: ${fsm_message_regex} " -l "fsm/fsm_test_upnp_plugin.sh" -tc
