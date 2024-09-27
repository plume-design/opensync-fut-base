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
configure_gatekeeper_policy.sh [-h] arguments
Description:
    - Script configures Gatekeeper rules to the OVSDB FSM_Policy table.
Arguments:
    -h  show this help message
Script usage example:
    ./configure_gatekeeper_policy.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_info_dump_line
    print_tables FSM_Policy
    fut_info_dump_line
' EXIT INT TERM

insert_ovsdb_entry FSM_Policy \
    -i policy gatekeeper \
    -i name gk_all \
    -i action gatekeeper \
    -i log all &&
        log "configure_gatekeeper_policy.sh: gk_all inserted to FSM_Policy inserted - Success" ||
        raise "Failed to insert gk_all to FSM_Policy" -l "configure_gatekeeper_policy.sh" -fc

pass
