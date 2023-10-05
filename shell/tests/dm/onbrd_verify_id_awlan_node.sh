#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_id_awlan_node.sh [-h] arguments
Description:
    - Validate AWLAN_Node id field
Arguments:
    -h  show this help message
    \$1 (dut_mac)   : MAC address of the DUT : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_id_awlan_node.sh <MAC_ADDR>
Script usage example:
    ./onbrd/onbrd_verify_id_awlan_node.sh 11:22:33:44:55:66
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_id_awlan_node.sh" -arg
dut_mac=${1}

trap '
fut_info_dump_line
print_tables AWLAN_Node
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "onbrd/onbrd_verify_id_awlan_node.sh: ONBRD test - Verify id field in AWLAN_Node table"

node_id=$(get_ovsdb_entry_value AWLAN_Node id -r)
serial_num=$(get_ovsdb_entry_value AWLAN_Node serial_number -r)

check_id_pattern "${node_id}" "${dut_mac}" "${serial_num}"
[ $? -eq 0 ] &&
    log "onbrd/onbrd_verify_id_awlan_node.sh: AWLAN_Node::id is valid - Success" ||
    raise "FAIL: AWLAN_Node::id is not valid" -l "onbrd/onbrd_verify_id_awlan_node.sh" -tc

pass
