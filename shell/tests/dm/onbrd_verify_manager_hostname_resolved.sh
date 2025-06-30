#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
onbrd/onbrd_verify_manager_hostname_resolved.sh [-h] arguments
Description:
    - Validate AWLAN_Node manager_addr being resolved in Manager target
Arguments:
    -h  show this help message
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

log_title "onbrd/onbrd_verify_manager_hostname_resolved.sh: ONBRD test - Verify if AWLAN_Node manager address hostname is resolved"

# Restart managers to start every config resolution from the beginning
restart_managers
# Give time to managers to bring up tables
sleep 30

wait_for_function_response 'notempty' "get_ovsdb_entry_value AWLAN_Node redirector_addr" &&
    redirector_addr=$(get_ovsdb_entry_value AWLAN_Node redirector_addr) ||
    raise "AWLAN_Node::redirector_addr is not set" -l "onbrd/onbrd_verify_manager_hostname_resolved.sh" -tc

if wan_link_selection_enabled; then
    redirector_addr_none="ssl:none:443"
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
