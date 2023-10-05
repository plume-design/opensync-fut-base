#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
device_mode_default="not_set"
usage()
{
cat << usage_string
dm/dm_verify_device_mode_awlan_node.sh [-h] arguments
Description:
    - Validate device mode value in AWLAN_Node table
Arguments:
    -h  show this help message
    \$1 (device_mode) : Used as value to check for in AWLAN_Node table : (string)(optional) : (default:${device_mode_default})
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_device_mode_awlan_node.sh <DEVICE-MODE>
Script usage example:
    ./dm/dm_verify_device_mode_awlan_node.sh ${device_mode_default}
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

device_mode=${1:-"${device_mode_default}"}

log_title "dm/dm_verify_device_mode_awlan_node.sh: ONBRD test - Verify device mode in AWLAN_Node"

if [ "$device_mode" = "not_set" ]; then
    wait_ovsdb_entry AWLAN_Node -is device_mode "[\"set\",[]]" &&
        log "dm/dm_verify_device_mode_awlan_node.sh: wait_ovsdb_entry - AWLAN_Node::device_mode is '[\"set\",[]]' - Success" ||
        raise "FAIL: wait_ovsdb_entry - AWLAN_Node::device_mode is not '$device_mode'" -l "dm/dm_verify_device_mode_awlan_node.sh" -tc
else
    wait_ovsdb_entry AWLAN_Node -is device_mode "$device_mode" &&
        log "dm/dm_verify_device_mode_awlan_node.sh: wait_ovsdb_entry - AWLAN_Node::device_mode is '$device_mode' - Success" ||
        raise "FAIL: wait_ovsdb_entry - AWLAN_Node::device_mode is not '$device_mode'" -l "dm/dm_verify_device_mode_awlan_node.sh" -tc
fi

pass
