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
onbrd/onbrd_verify_fw_version_awlan_node.sh [-h] arguments
Description:
    Validate firmware_version field in table AWLAN_Node.
    The test script acquires the FW version string from the device and
    verifies it using the specified method.
Arguments:
    -h              : show this help message
    \$1 match_rule  : how to verify that the FW version string is valid: (string)(required)
                    : Options:
                    :   - non_empty(default): only verify that the version string is present and not empty
                    :   - pattern_match     : match the version string with the requirements set by the cloud
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_fw_version_awlan_node.sh match_rule
Script usage example:
    ./onbrd/onbrd_verify_fw_version_awlan_node.sh non_empty
    ./onbrd/onbrd_verify_fw_version_awlan_node.sh pattern_match
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

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_fw_version_awlan_node.sh" -arg
match_rule=${1:-"non_empty"}

log_title "onbrd/onbrd_verify_fw_version_awlan_node.sh: ONBRD test - Verify FW version string in AWLAN_Node '${match_rule}'"

# TESTCASE:
fw_version_string=$(get_ovsdb_entry_value AWLAN_Node firmware_version -r)
log "onbrd/onbrd_verify_fw_version_awlan_node.sh: Verifying FW version string '${fw_version_string}' for rule: '${match_rule}'"

if [ "${match_rule}" = "non_empty" ]; then
    log "onbrd/onbrd_verify_fw_version_awlan_node.sh: FW version string must not be empty"
    [ "${fw_version_string}" = "" ] &&
        raise "FW version string is empty" -l "onbrd/onbrd_verify_fw_version_awlan_node.sh" -tc ||
        log "onbrd/onbrd_verify_fw_version_awlan_node.sh: FW version string is not empty - Success"
elif [ "${match_rule}" = "pattern_match" ]; then
    log "onbrd/onbrd_verify_fw_version_awlan_node.sh: FW version string must match parsing rules and regular expression"
    check_fw_pattern "${fw_version_string}" &&
        log "onbrd/onbrd_verify_fw_version_awlan_node.sh: FW version string is valid - Success" ||
        raise "FW version string is not valid" -l "onbrd/onbrd_verify_fw_version_awlan_node.sh" -tc
else
    raise "Invalid match_rule '${match_rule}', must be 'non_empty' or 'pattern_match'" -l "onbrd/onbrd_verify_fw_version_awlan_node.sh" -arg
fi

pass
