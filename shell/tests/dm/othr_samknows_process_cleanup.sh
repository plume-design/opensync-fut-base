#!/bin/sh

# Clean up after tests for OTHR.

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
othr/othr_samknows_process_cleanup.sh [-h] arguments
Description:
    - Script removes samknows module from Node_Config table.
Arguments:
    -h : show this help message
Script usage example:
    ./othr/othr_samknows_process_cleanup.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_samknows_process_cleanup.sh" -arg

log "othr/othr_samknows_process_cleanup.sh: Clean up samknows module from Node_Config table"

remove_ovsdb_entry Node_Config -w module "samknows" &&
    log "othr/othr_samknows_process_cleanup.sh: remove_ovsdb_entry - Removed entry for 'samknows' from Node_Config table - Success" ||
    log -err "othr/othr_samknows_process_cleanup.sh: Failed to remove entry for 'samknows' from Node_Config table"

print_tables Node_Config

pass
