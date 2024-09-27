#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="tpsm/tpsm_setup.sh"
usage()
{
cat << usage_string
tpsm/tpsm_verify_samknows_process.sh [-h] arguments
Description:
    - Script verifies if samknows feature is triggered on DUT.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./tpsm/tpsm_verify_samknows_process.sh
Script usage example:
    ./tpsm/tpsm_verify_samknows_process.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Node_Config Node_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

check_kconfig_option "3RDPARTY_SAMKNOWS" "y" ||
    raise "'Samknows' feature not supported on this device" -l "tpsm/tpsm_verify_samknows_process.sh" -s

log_title "tpsm/tpsm_verify_samknows_process.sh: TPSM test - Verify Samknows process is triggered on DUT"

check_ovsdb_table_exist Node_Config ||
    raise "Node_Config table does not exist in ovsdb" -l "tpsm/tpsm_verify_samknows_process.sh" -s

${OVSH} U Node_Config -w module==samknows value:=\"true\" key:=enable &&
    log "tpsm/tpsm_verify_samknows_process.sh: Upsert - Node_Config::value and Node_Config::key are inserted - Success" ||
    raise "Upsert - Node_Config::value and Node_Config::key failed to insert" -l "tpsm/tpsm_verify_samknows_process.sh" -fc

wait_ovsdb_entry Node_State -w module "samknows" -is value \"true\" -is key enable &&
    log "tpsm/tpsm_verify_samknows_process.sh: wait_ovsdb_entry - Node_State::value and Node_State::key are updated - Success" ||
    raise "wait_ovsdb_entry - Node_State::value and Node_State::key failed to update" -l "tpsm/tpsm_verify_samknows_process.sh" -tc

pgrep "samknows" &> /dev/null &&
    log "tpsm/tpsm_verify_samknows_process.sh: Samknows process is running on the DUT - Success" ||
    raise "Samknows process failed to run on DUT" -l "tpsm/tpsm_verify_samknows_process.sh" -tc

remove_ovsdb_entry Node_Config -w module "samknows" &&
    log "tpsm/tpsm_verify_samknows_process.sh: remove_ovsdb_entry - Removed entry for 'samknows' from Node_Config table - Success" ||
    raise "remove_ovsdb_entry - Failed to remove entry for 'samknows' from Node_Config table" -l "tpsm/tpsm_verify_samknows_process.sh" -tc

pass
