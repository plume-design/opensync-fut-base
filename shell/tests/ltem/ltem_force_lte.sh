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
ltem/ltem_force_lte.sh [-h] arguments
Description:
    - This script is used to force switch to LTE for LTEM testing.
Arguments:
    -h : show this help message
    \$1 (lte_if_name)  : lte interface name  : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./ltem/ltem_force_lte.sh <lte_if_name>
Script usage example:
    ./ltem/ltem_force_lte.sh wwan0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "ltem/ltem_force_lte.sh" -arg
lte_if_name=${1}

trap '
    fut_info_dump_line
    print_tables Lte_Config Lte_State
    fut_info_dump_line
' EXIT INT TERM

check_ovsdb_table_exist Lte_Config &&
    log "ltem/ltem_force_lte.sh: Lte_Config table exists in OVSDB - Success" ||
    raise "Lte_Config table does not exist in OVSDB" -l "ltem/ltem_force_lte.sh" -s

update_ovsdb_entry Lte_Config -w if_name "$lte_if_name" \
    -u force_use_lte "true" &&
        log "ltem/ltem_force_lte.sh: update_ovsdb_entry - Lte_Config::force_use_lte set to 'true' - Success" ||
        raise "update_ovsdb_entry - Lte_Config::force_use_lte not set to 'true'" -l "ltem/ltem_force_lte.sh" -tc

check_ovsdb_table_exist Lte_State &&
    log "ltem/ltem_force_lte.sh: Lte_State table exists in OVSDB - Success" ||
    raise "Lte_State table does not exist in OVSDB" -l "ltem/ltem_force_lte.sh" -s

wait_ovsdb_entry Lte_State -w if_name "$lte_if_name" -is force_use_lte true &&
    log "ltem/ltem_force_lte.sh: wait_ovsdb_entry - Lte_Config reflected to Lte_State::force_use_lte is 'true' - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Lte_Config to Lte_State::force_use_lte is not 'true'" -l "ltem/ltem_force_lte.sh" -tc

update_ovsdb_entry Lte_Config -w if_name "$lte_if_name" \
    -u force_use_lte "false" &&
        log "ltem/ltem_force_lte.sh: update_ovsdb_entry - Lte_Config::force_use_lte set to 'false' - Success" ||
        raise "update_ovsdb_entry - Lte_Config::force_use_lte not set to 'false'" -l "ltem/ltem_force_lte.sh" -tc

wait_ovsdb_entry Lte_State -w if_name "$lte_if_name" -is force_use_lte false &&
    log "ltem/ltem_force_lte.sh: wait_ovsdb_entry - Lte_Config reflected to Lte_State::force_use_lte is 'false' - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Lte_Config to Lte_State::force_use_lte is not 'false'" -l "ltem/ltem_force_lte.sh" -tc

pass
