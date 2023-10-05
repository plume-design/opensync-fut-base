#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

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
fut_info_dump_line
if [ $fut_ec -ne 0 ]; then 
    print_tables Wifi_Associated_Clients
    check_restore_ovsdb_server
fi
fut_info_dump_line
exit $fut_ec
' EXIT SIGINT SIGTERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument" -arg
client_mac=${1}

log_title "tools/device/check_wifi_client_associated.sh: Verify that the client is associated to AP"

check_ovsdb_entry Wifi_Associated_Clients -w mac "$client_mac"
if [ $? -eq 0 ]; then
    log "tools/device/check_wifi_client_associated.sh: Valid client mac $client_mac is populated in the Wifi_Associated_Clients table - Success"
    exit 0
else
    log "tools/device/check_wifi_client_associated.sh: Client mac address $client_mac is not populated in the Wifi_Associated_Clients table."
    exit 1
fi

