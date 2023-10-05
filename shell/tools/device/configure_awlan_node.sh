#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat << usage_string
configure_awlan_node.sh [-h] arguments
Description:
    - Script configures AWLAN_Node table
Arguments:
    -h  show this help message

Script usage example:
    ./configure_awlan_node.sh <LOCATION_ID> <NODE_ID>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables AWLAN_Node
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
location_id=${1}
node_id=${2}

${OVSH} u AWLAN_Node mqtt_headers:ins:"[\"map\",[[\"locationId\",\"${location_id}\"]]]"
${OVSH} u AWLAN_Node mqtt_headers:ins:"[\"map\",[[\"nodeId\",\"${node_id}\"]]]"

pass
