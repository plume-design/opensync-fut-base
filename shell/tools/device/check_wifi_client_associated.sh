#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat <<usage_string
tools/device/check_wifi_client_associated.sh [-h] arguments
Description:
    - Script verifies Wifi_Associated_Clients table is populated with client's mac.
Arguments:
    -h  show this help message
    \$1  (client_mac)     : MAC address of client connected to ap: (string)(required)
Script usage example:
    ./tools/device/check_wifi_client_associated.sh a1:b2:c3:d4:e5:f6
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables Wifi_Associated_Clients
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument" -arg
client_mac=${1}

log_title "tools/device/check_wifi_client_associated.sh: Verify that the client is associated to AP"

wait_ovsdb_entry Wifi_Associated_Clients -w mac "$client_mac" &&
    log "tools/device/check_wifi_client_associated.sh: Valid client mac $client_mac is populated in the Wifi_Associated_Clients table - Success" ||
    raise "Client mac address $client_mac is not populated in the Wifi_Associated_Clients table." -l "tools/device/check_wifi_client_associated.sh" -tc
