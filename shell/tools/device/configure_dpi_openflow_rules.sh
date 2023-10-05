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
fsm/configure_dpi_openflow_rules.sh [-h] arguments
Description:
    Script inserts rules to the OVSDB Openflow_Config table.
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

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
bridge=${1}

log_title "tools/device/configure_dpi_openflow_rules.sh: FSM test - Configure Openflow rules"

log "configure_dpi_openflow_rules.sh: Cleaning Openflow_Config table"
empty_ovsdb_table Openflow_Config

dev_token="dev_test"
of_port=30001

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 0 \
    -i priority 0 \
    -i bridge "${bridge}" \
    -i action normal &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 1 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 0 \
    -i priority 200 \
    -i bridge "${bridge}" \
    -i action "resubmit(,7)" &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 2 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 7 \
    -i priority 0 \
    -i bridge "${bridge}" \
    -i action normal &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 3 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 7 \
    -i priority 200 \
    -i bridge "${bridge}" \
    -i rule "ct_state=-trk,ip" \
    -i action "ct(table=7,zone=1)" &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 4 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 7 \
    -i priority 200 \
    -i bridge "${bridge}" \
    -i rule "ct_state=+trk,ct_mark=0,ip" \
    -i action "ct(commit,zone=1,exec(load:0x1->NXM_NX_CT_MARK[])),NORMAL,output:${of_port}" &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 5 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 7 \
    -i priority 200 \
    -i bridge "${bridge}" \
    -i rule "ct_zone=1,ct_state=+trk,ct_mark=1,ip" \
    -i action "NORMAL,output:${of_port}" &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 6 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 7 \
    -i priority 200 \
    -i bridge "${bridge}" \
    -i rule "ct_zone=1,ct_state=+trk,ct_mark=2,ip" \
    -i action "NORMAL" &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 7 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

insert_ovsdb_entry Openflow_Config \
    -i token "${dev_token}" \
    -i table 7 \
    -i priority 200 \
    -i bridge "${bridge}" \
    -i rule "ct_state=+trk,ct_mark=3,ip" \
    -i action "DROP" &&
        log "configure_dpi_openflow_rules.sh: Openflow rule 8 inserted - Success" ||
        raise "FAIL: Failed to insert Openflow rule" -l "configure_dpi_openflow_rules.sh" -oe

pass
