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
dm/dm_verify_opensync_version_awlan_node.sh [-h] arguments
Description:
    - Validate OpenSync version information availability in AWLAN_Node table.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_opensync_version_awlan_node.sh
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

log_title "dm/dm_verify_opensync_version_awlan_node.sh: DM test - Verify OpenSync version in AWLAN_Node"

wait_for_function_response 0 "${OVSH} s AWLAN_Node -j | grep -q OPENSYNC" &&
    log "dm/dm_verify_opensync_version_awlan_node.sh: OpenSync version information exists - Success" ||
    raise "FAIL: OpenSync version information does not exist in AWLAN_Node"  -l "dm/dm_verify_opensync_version_awlan_node.sh" -tc

pass
