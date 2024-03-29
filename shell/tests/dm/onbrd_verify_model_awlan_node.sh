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
onbrd/onbrd_verify_model_awlan_node.sh [-h] arguments
Description:
    - Validate AWLAN_Node model field
Arguments:
    -h  show this help message
    \$1 (model) : used as model to verify correct model entry : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_model_awlan_node.sh <MODEL>
Script usage example:
    ./onbrd/onbrd_verify_model_awlan_node.sh PP203X
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_model_awlan_node.sh" -arg
expected_model=$1

trap '
fut_info_dump_line
print_tables AWLAN_Node
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "onbrd/onbrd_verify_model_awlan_node.sh: ONBRD test - Verify model in AWLAN_Node, waiting for '$expected_model' string"

log "onbrd/onbrd_verify_model_awlan_node.sh: Verify model, waiting for '$expected_model'"
wait_for_function_response 0 "check_ovsdb_entry AWLAN_Node -w model \"'$expected_model'\"" &&
    log "onbrd/onbrd_verify_model_awlan_node.sh: AWLAN_Node::model is '$expected_model' - Success" ||
    raise "FAIL: AWLAN_Node::model is not '$expected_model'" -l "onbrd/onbrd_verify_model_awlan_node.sh" -tc

model_string=$(get_ovsdb_entry_value AWLAN_Node model -r)
log "onbrd/onbrd_verify_model_awlan_node.sh: Check the model string for allowed characters."
check_model_pattern "${model_string}" &&
    log "onbrd/onbrd_verify_model_awlan_node.sh: AWLAN_Node::model is valid - Success" ||
    raise "FAIL: AWLAN_Node::model is not valid" -l "onbrd/onbrd_verify_model_awlan_node.sh" -tc

pass
