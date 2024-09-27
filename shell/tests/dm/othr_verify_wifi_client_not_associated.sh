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
othr/othr_verify_wifi_client_not_associated.sh [-h] arguments
Description:
    - Script checks if wireless client is not connected to DUT.
Arguments:
    -h  show this help message
Script usage example:
    ./othr/othr_verify_wifi_client_not_associated.sh
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
    print_tables Wifi_Radio_State
    print_tables Wifi_VIF_State
    print_tables Wifi_Inet_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "othr/othr_verify_wifi_client_not_associated.sh: OTHR test - Connect associated client"

log "othr/othr_verify_wifi_client_not_associated.sh - Print-out Wifi_Associated_Clients table"
print_tables Wifi_Associated_Clients

client_mac=$(get_ovsdb_entry_value Wifi_Associated_Clients mac)
if [ -z "${client_mac}" ]; then
    client_mac="${client_mac%%,*}"
    log "othr/othr_verify_wifi_client_not_associated.sh - Client $client_mac not connected - Success"
else
    raise "Client MAC address acquired from Wifi_Associated_Clients" -l "othr/othr_verify_wifi_client_not_associated.sh"
fi

pass
