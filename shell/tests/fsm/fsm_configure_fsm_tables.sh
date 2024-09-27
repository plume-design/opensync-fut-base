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
fsm/fsm_configure_fsm_tables.sh [-h] arguments
Description:
    - Script configures FSM settings to Flow_Service_Manager_Config
Arguments:
    -h  show this help message
    \$1 (lan_bridge_if_name) : used as bridge interface name         : (string)(required)
    \$2 (postfix)            : used as postfix on tap interface name : (string)(required)
    \$3 (handler)            : used as handler at fsm tables         : (string)(required)
    \$4 (plugin)             : used as plugin at fsm tables          : (string)(required)
Script usage example:
    ./fsm/fsm_configure_fsm_tables.sh br-home tdns dev_dns /usr/opensync/lib/libfsm_dns.so
    ./fsm/fsm_configure_fsm_tables.sh br-home thttp dev_http /usr/opensync/lib/libfsm_http.so
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Openflow_Config
    print_tables Flow_Service_Manager_Config FSM_Policy
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=4
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
lan_bridge_if_name=${1}
tap_name_postfix=${2}
handler=${3}
plugin=${4}

# Construct from input arguments
tap_if_name="${lan_bridge_if_name}.${tap_name_postfix}"

log_title "fsm/fsm_configure_fsm_tables.sh: FSM test - Configuring FSM tables required for FSM testing - $tap_if_name - $plugin"

log "fsm/fsm_configure_fsm_tables.sh: Cleaning FSM OVSDB Config tables"
empty_ovsdb_table Openflow_Config
empty_ovsdb_table Flow_Service_Manager_Config
empty_ovsdb_table FSM_Policy

insert_ovsdb_entry Flow_Service_Manager_Config \
    -i if_name "${tap_if_name}" \
    -i handler "$handler" \
    -i plugin "$plugin" &&
        log "fsm/fsm_configure_fsm_tables.sh: Flow_Service_Manager_Config entry added - Success" ||
        raise "insert_ovsdb_entry - Failed to insert Flow_Service_Manager_Config entry" -l "fsm/fsm_configure_fsm_tables.sh" -fc

# Removing entry
remove_ovsdb_entry Flow_Service_Manager_Config -w if_name "${tap_if_name}" &&
    log "fsm/fsm_configure_fsm_tables.sh: remove_ovsdb_entry - Removed entry for ${tap_if_name} from Flow_Service_Manager_Config - Success" ||
    raise "remove_ovsdb_entry - Failed to remove entry for ${tap_if_name} from Flow_Service_Manager_Config" -l "fsm/fsm_configure_fsm_tables.sh" -fc

pass
