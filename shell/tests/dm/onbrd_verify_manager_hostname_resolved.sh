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
onbrd/onbrd_verify_manager_hostname_resolved.sh [-h] arguments
Description:
    - Validate AWLAN_Node manager_addr being resolved in Manager target
Arguments:
    -h  show this help message
    \$1 is_extender : 'true' - device is an extender, 'false' - device is a residential_gateway : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_manager_hostname_resolved.sh <true/false>
Script usage example:
    ./onbrd/onbrd_verify_manager_hostname_resolved.sh true    #if device is a extender
    ./onbrd/onbrd_verify_manager_hostname_resolved.sh false   #if device is a gateway
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables AWLAN_Node Manager
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -arg
is_extender=${1}

if [ $is_extender == "true" ]; then
    check_kconfig_option "TARGET_CAP_EXTENDER" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Device is not EXTENDER capable" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -s
elif [ $is_extender == "false" ]; then
    check_kconfig_option "TARGET_CAP_GATEWAY" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Device is not a Gateway" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -s
else
    raise "Wrong option" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -s
fi

log_title "onbrd/onbrd_verify_manager_hostname_resolved.sh: ONBRD test - Verify if AWLAN_Node manager address hostname is resolved"

# Restart managers to start every config resolution from the beginning
restart_managers
# Give time to managers to bring up tables
sleep 30

redirector_addr_none="ssl:none:443"
wait_for_function_response 'notempty' "get_ovsdb_entry_value AWLAN_Node redirector_addr" &&
    redirector_addr=$(get_ovsdb_entry_value AWLAN_Node redirector_addr) ||
    raise "AWLAN_Node::redirector_addr is not set" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -tc

if [ $is_extender == "true" ]; then
    log "onbrd/onbrd_verify_manager_hostname_resolved.sh: Setting AWLAN_Node redirector_addr to ${redirector_addr_none}"
    update_ovsdb_entry AWLAN_Node -u redirector_addr "${redirector_addr_none}" &&
        log "onbrd/onbrd_verify_manager_hostname_resolved.sh: AWLAN_Node::redirector_addr updated - Success" ||
        raise "Could not update AWLAN_Node::redirector_addr" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -fc

    log "onbrd/onbrd_verify_manager_hostname_resolved.sh: Wait Manager target to clear"
    wait_for_function_response 'empty' "get_ovsdb_entry_value Manager target" &&
        log "onbrd/onbrd_verify_manager_hostname_resolved.sh: Manager::target is cleared - Success" ||
        raise "Manager::target is not cleared" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -tc

    log "onbrd/onbrd_verify_manager_hostname_resolved.sh: Setting AWLAN_Node redirector_addr to ${redirector_addr}"
    update_ovsdb_entry AWLAN_Node -u redirector_addr "${redirector_addr}" &&
        log "onbrd/onbrd_verify_manager_hostname_resolved.sh: AWLAN_Node::redirector_addr updated - Success" ||
        raise "Could not update AWLAN_Node::redirector_addr" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -fc
fi

log "onbrd/onbrd_verify_manager_hostname_resolved.sh: Wait Manager target to resolve to address"
wait_for_function_response 'notempty' "get_ovsdb_entry_value Manager target" &&
    log "onbrd/onbrd_verify_manager_hostname_resolved.sh: Manager::target is set - Success" ||
    raise "Manager::target is not set" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -tc

print_tables Manager
pass
