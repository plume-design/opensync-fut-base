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
othr/othr_connect_wifi_client_to_ap_unfreeze.sh [-h] arguments
Description:
    - Script removes client freeze rules from Openflow tables (Openflow_Tag, Openflow_Config).
Arguments:
    -h  show this help message
Script usage example:
    ./othr/othr_connect_wifi_client_to_ap_unfreeze.sh
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

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input arguments" -arg

log_title "othr/othr_connect_wifi_client_to_ap_unfreeze.sh: OTHR test - Delete the Openflow rules from the tables to unfreeze the client"

log "othr/othr_connect_wifi_client_to_ap_unfreeze.sh: Removing client freeze rules from Openflow tables"

remove_ovsdb_entry Openflow_Tag -w name "frozen" &&
    log "othr/othr_connect_wifi_client_to_ap_unfreeze.sh: Removed entry for name 'frozen' from Openflow_Tag table - Success" ||
    raise "Could not remove entry for name 'frozen' from Openflow_Tag table" -l "othr/othr_connect_wifi_client_to_ap_unfreeze.sh"

if ! linux_native_bridge_enabled; then
    remove_ovsdb_entry Openflow_Config -w token "${freeze_src_token}" &&
        log "othr/othr_connect_wifi_client_to_ap_unfreeze.sh: Removed entry for token '${freeze_src_token}' from Openflow_Config table - Success" ||
        raise "Could not remove entry for token '${freeze_src_token}' from Openflow_Config table" -l "othr/othr_connect_wifi_client_to_ap_unfreeze.sh"

    remove_ovsdb_entry Openflow_Config -w token "${freeze_dst_token}" &&
        log "othr/othr_connect_wifi_client_to_ap_unfreeze.sh: Removed entry for token '${freeze_dst_token}' from Openflow_Config table - Success" ||
        raise "Could not remove entry for token '${freeze_dst_token}' from Openflow_Config table" -l "othr/othr_connect_wifi_client_to_ap_unfreeze.sh"
fi

pass
