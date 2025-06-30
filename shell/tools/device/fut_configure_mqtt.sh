#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat << usage_string
tools/device/fut_configure_mqtt.sh [-h] arguments
Description:
    - Script configures MQTT settings in AWLAN_Node table
Arguments:
    -h  show this help message
    \$1 (hostname)    : MQTT hostname                          : (string)(required)
    \$2 (port)        : MQTT port                              : (string)(required)
    \$3 (location_id) : locationId for AWLAN_Node:mqtt_headers : (string)(required)
    \$4 (node_id)     : nodeId for AWLAN_Node:mqtt_headers     : (string)(required)
    \$5 (topics)      : topics for AWLAN_Node:mqtt_settings    : (string)(required)
    \$6 (mqtt_topics_key) : topics key in AWLAN_Node:mqtt_topics : (string)(optional)
Script usage example:
    ./tools/device/fut_configure_mqtt.sh 192.168.200.1 65002 1000 100 http
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables AWLAN_Node SSL
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=5
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
hostname=${1}
port=${2}
location_id=${3}
node_id=${4}
topics=${5}
mqtt_topics_key=${6}
ca_cert_path=$(get_ovsdb_entry_value SSL ca_cert)
fut_server_cert_path="${FUT_TOPDIR}/shell/tools/server/certs/ca.pem"

cat "${fut_server_cert_path}" > "${ca_cert_path}"

log "tools/device/fut_configure_mqtt.sh: Configuring MQTT AWLAN_Node settings"
update_ovsdb_entry AWLAN_Node \
    -u mqtt_settings '["map",[["broker","'"${hostname}"'"],["compress","zlib"],["port","'"${port}"'"],["topics","'"${topics}"'"]]]' \
    -u mqtt_headers '["map",[["locationId","'"${location_id}"'"],["nodeId","'"${node_id}"'"]]]'

if [ -n "${mqtt_topics_key}" ] ; then
    log "tools/device/fut_configure_mqtt.sh: Configuring MQTT AWLAN_Node::mqtt_topics"
    update_ovsdb_entry AWLAN_Node \
        -u mqtt_topics '["map",[["'"${mqtt_topics_key}"'","'"${topics}"'"]]]'
fi

log "tools/device/fut_configure_mqtt.sh: Restarting QM manager to instantly reconnects"
killall qm &&
    log "tools/device/fut_configure_mqtt.sh: QM killed" ||
    log "tools/device/fut_configure_mqtt.sh: QM not running, nothing to kill"

start_specific_manager qm &&
    log "tools/device/fut_configure_mqtt.sh: QM killed" ||
    raise "to start QM manager" -ds -l "tools/device/fut_configure_mqtt.sh"

set_manager_log QM TRACE ||
    raise "set_manager_log QM TRACE" -l "tools/device/fut_configure_mqtt.sh" -ds
