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
onbrd/onbrd_verify_redirector_address_awlan_node.sh [-h] arguments
Description:
    - Validate redirector address in AWLAN_Node table
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_redirector_address_awlan_node.sh
Script usage example:
    ./onbrd/onbrd_verify_redirector_address_awlan_node.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables AWLAN_Node
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "onbrd/onbrd_verify_redirector_address_awlan_node.sh: ONBRD test - Verify redirector address"

wait_for_function_response 'notempty' "get_ovsdb_entry_value AWLAN_Node redirector_addr" &&
    check_pass=true ||
    check_pass=false

print_tables AWLAN_Node

[ "${check_pass}" = true ] &&
    log "onbrd/onbrd_verify_redirector_address_awlan_node.sh: AWLAN_Node::redirector_addr is populated - Success" ||
    raise "AWLAN_Node::redirector_addr is not populated" -l "onbrd/onbrd_verify_redirector_address_awlan_node.sh" -tc
pass
