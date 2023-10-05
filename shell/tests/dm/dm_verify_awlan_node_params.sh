#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_awlan_node_params.sh [-h] arguments
Description:
    - Verify if the provided field in AWLAN_Node table exists and is populated. Test is skipped if it does not exist.
Arguments:
    -h  show this help message
    \$1 (awlan_node_field)     : field to verify if it exists in the awlan_node table           : (string)(required)
    \$2 (awlan_node_field_val) : field value to verify if its populated in the awlan_node table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_awlan_node_params.sh <alwan_field_name> <alwan_field_val>
Script usage example:
    ./dm/dm_verify_awlan_node_params.sh vendor_factory notempty
    ./dm/dm_verify_awlan_node_params.sh vendor_name OpenSync

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
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input arguments" -l "dm/dm_verify_awlan_node_params.sh" -arg
awlan_node_field=${1}
awlan_node_field_val=${2}

log_title "dm/dm_verify_awlan_node_params.sh: DM test - Verify AWLAN_Node fields exist and are non empty"

print_tables AWLAN_Node

check_ovsdb_table_field_exists AWLAN_Node "$awlan_node_field" ||
    raise "AWLAN_Node::$awlan_node_field field does not exist for this OpenSync version" -l "dm/dm_verify_awlan_node_params.sh" -s

if [ "$awlan_node_field_val" = "notempty" ]
then
    wait_for_function_response "$awlan_node_field_val" "get_ovsdb_entry_value AWLAN_Node $awlan_node_field" 5 &&
        log "dm/dm_verify_awlan_node_params.sh: AWLAN_Node::$awlan_node_field is populated - Success" ||
        raise "FAIL: AWLAN_Node::$awlan_node_field is empty" -l "dm/dm_verify_awlan_node_params.sh" -tc
else
    wait_ovsdb_entry AWLAN_Node -is vendor_name "$awlan_node_field_val" &&
    log "dm/dm_verify_awlan_node_params.sh: AWLAN_Node::$awlan_node_field equals expected '$awlan_node_field_val' - Success" ||
    raise "FAIL: AWLAN_Node::$awlan_node_field does not equal expected '$awlan_node_field_val'"  -l "dm/dm_verify_awlan_node_params.sh" -tc
fi

pass
