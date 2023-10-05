#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
fsm/fsm_configure_of_rules.sh [-h] arguments
Description:
    - Script insert rule to Openflow table as a part of fsm plugin configuration.

Arguments:
    -h  show this help message
    \$1 (lan_bridge_if) : used as bridge interface name                      : (string)(required)
    \$2 (action)        : used as Openflow action to perform on traffic flow : (string)(required)
    \$3 (rule)          : used as Openflow rule                              : (string)(required)
    \$4 (token)         : used as Openflow token                             : (string)(required)

Script usage example:
    ./fsm/fsm_configure_of_rules.sh br-home normal,output:3001 udp,tp_dst=53 dev_flow_dns_out
    ./fsm/fsm_configure_of_rules.sh br-home normal,output:4001 tcp,tcp_dst=80 dev_flow_http_out
    ./fsm/fsm_configure_of_rules.sh br-home output:5001 udp,tp_dst=53 dev_flow_upnp_out
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Openflow_Config Openflow_State
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=4
[ $# -lt ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
lan_bridge_if=${1}
action=${2}
rule=${3}
token=${4}

client_mac="ab:12:cd:34:ef:56"

# Construct from input arguments
of_req_rule="dl_src=${client_mac},${rule}"

log_title "fsm/fsm_configure_of_rules.sh: FSM test - Configure Openflow rules - $rule"

log "fsm/fsm_configure_of_rules.sh: Cleaning FSM OVSDB Config table"
empty_ovsdb_table Openflow_Config

# Insert rule to Openflow_Config
insert_ovsdb_entry Openflow_Config \
    -i bridge "$lan_bridge_if" \
    -i action "$action" \
    -i priority 200 \
    -i table 0 \
    -i rule "$of_req_rule" \
    -i token "$token" &&
        log "fsm/fsm_configure_of_rules.sh: Openflow rule inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "fsm/fsm_configure_of_rules.sh" -oe

# Check if rule is applied
log "fsm/fsm_configure_of_rules.sh: Checking if rule is set for $of_req_rule"
wait_ovsdb_entry Openflow_State -w token "$token" -is success true &&
    log "fsm/fsm_configure_of_rules.sh: wait_ovsdb_entry - Rule is set - Openflow_State::success is 'true' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to set rule - Openflow_State::success for '$token' is not 'true'" -l "fsm/fsm_configure_of_rules.sh" -tc

# Removing entry
remove_ovsdb_entry Openflow_Config -w bridge "${lan_bridge_if}" &&
    log "fsm/fsm_configure_of_rules.sh: remove_ovsdb_entry - Removed entry for ${lan_bridge_if} from Openflow_Config - Success" ||
    raise "FAIL: remove_ovsdb_entry - Failed to remove entry for ${lan_bridge_if} from Openflow_Config" -l "fsm/fsm_configure_of_rules.sh" -oe

empty_ovsdb_table Openflow_Config
empty_ovsdb_table Openflow_State

pass
