#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091,SC2016
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat << usage_string
configure_dpi_sni_plugin.sh [-h] arguments
Description:
    Script configures FSM settings for:
        - Walleye
        - DPI SNI client
        - Gatekeeper and
        - dispatcher to Flow_Service_Manager_Config.
Arguments:
    -h  show this help message
    \$1 (topic)  : MQTT topic  : (string)(required)
Script usage example:
    ./configure_dpi_sni_plugin.sh  <LOCATION_ID> <NODE_ID>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_info_dump_line
    print_tables Flow_Service_Manager_Config
    fut_info_dump_line
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
topic=${1}

# Configure Walleye DPI
insert_ovsdb_entry Flow_Service_Manager_Config \
    -i handler walleye_dpi \
    -i type dpi_plugin \
    -i other_config "[\"map\",[[\"dpi_dispatcher\",\"core_dpi_dispatch\"],[\"dso_init\",\"walleye_dpi_plugin_init\"],[\"mqtt_v\",\"'${topic}'\"]]]" &&
        log "configure_dpi_sni_plugin.sh: Walleye DPI configuration inserted to Flow_Service_Manager_Config - Success" ||
        raise "Failed to insert Walleye DPI configuration to Flow_Service_Manager_Config" -l "configure_dpi_sni_plugin.sh" -fc

# Configure DPI SNI client
insert_ovsdb_entry Flow_Service_Manager_Config \
    -i handler dpi_sni \
    -i type dpi_client \
    -i other_config '["map",[["dpi_plugin","walleye_dpi"],["dso_init","dpi_sni_plugin_init"],["flow_attributes","${walleye_sni_attrs}"],["policy_table","gatekeeper"],["provider_plugin","gatekeeper"],["mqtt_v","'${topic}'"]]]' &&
        log "configure_dpi_sni_plugin.sh: DPI SNI client configuration inserted to Flow_Service_Manager_Config - Success" ||
        raise "Failed to insert DPI SNI client configuration to Flow_Service_Manager_Config" -l "configure_dpi_sni_plugin.sh" -fc

# Configure Gatekeeper (Controller based Gatekeeper)
insert_ovsdb_entry Flow_Service_Manager_Config \
    -i handler gatekeeper \
    -i type web_cat_provider \
    -i other_config '["map",[["gk_url","https://fut.opensync.io:8443/gatekeeper"],["dso_init","gatekeeper_plugin_init"],["cacert","'${FUT_TOPDIR}'/shell/tools/server/certs/ca.pem"],["mqtt_v","'${topic}'"]]]' &&
        log "configure_dpi_sni_plugin.sh: Gatekeeper configuration inserted to Flow_Service_Manager_Config - Success" ||
        raise "Failed to insert Gatekeeper configuration to Flow_Service_Manager_Config" -l "configure_dpi_sni_plugin.sh" -fc

# Configure dispatcher
insert_ovsdb_entry Flow_Service_Manager_Config \
    -i handler core_dpi_dispatch \
    -i type dpi_dispatcher \
    -i if_name "br-home.dpi" \
    -i other_config '["map",[["excluded_devices","${all_gateways}"],["mqtt_v","'${topic}'"]]]' &&
        log "configure_dpi_sni_plugin.sh: Dispatcher configuration inserted to Flow_Service_Manager_Config - Success" ||
        raise "Failed to insert Dispatcher configuration to Flow_Service_Manager_Config" -l "configure_dpi_sni_plugin.sh" -fc

insert_ovsdb_entry Flow_Service_Manager_Config \
    -i handler dpi_dns \
    -i type dpi_client \
    -i other_config '["map",[["dpi_plugin","walleye_dpi"],["excluded_devices","${fm.dns-exclude}"],["flow_attributes","${fm.walleye_dns_attrs}"],["policy_table","gatekeeper"],["provider_plugin","gatekeeper"],["mqtt_v","'${topic}'"]]]' &&
        log "configure_dpi_sni_plugin.sh: DPI SNI client configuration inserted to Flow_Service_Manager_Config - Success" ||
        raise "Failed to insert DPI SNI client configuration to Flow_Service_Manager_Config" -l "configure_dpi_sni_plugin.sh" -fc

pass
