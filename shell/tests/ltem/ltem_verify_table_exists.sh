#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="ltem/ltem_setup.sh"

usage()
{
cat << usage_string
ltem/ltem_verify_table_exists.sh [-h] arguments
Description:
    - This script is used to verify Lte_Config and Lte_State tables exist.
Arguments:
    -h : show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./ltem/ltem_verify_table_exists.sh
Script usage example:
    ./ltem/ltem_verify_table_exists.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "ltem/ltem_validation.sh" -arg

trap '
fut_info_dump_line
print_tables Lte_Config Lte_State
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

check_ovsdb_table_exist Lte_Config &&
    log "ltem/ltem_verify_table_exists.sh: Lte_Config table exists in ovsdb - Success" ||
    raise "FAIL: Lte_Config table does not exist in ovsdb" -l "ltem/ltem_verify_table_exists.sh" -s

check_ovsdb_table_exist Lte_State &&
    log "ltem/ltem_verify_table_exists.sh: Lte_State table exists in ovsdb - Success" ||
    raise "FAIL: Lte_State table does not exist in ovsdb" -l "ltem/ltem_verify_table_exists.sh" -s

pass
