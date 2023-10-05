#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_node_services.sh [-h] arguments
Description:
    - Verify Node_Services table is correctly populated
    - Check if Node_Services table contains service from test case config
    - Check if Node_Services table having enable field for service is set
      to true and service is running
Arguments:
    -h  show this help message
    \$1 (service)     : service to verify : (string)(required)
    \$2 (kconfig_val) : kconfig value used to check service is supported on device or not : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_node_services.sh <service> <KCONFIG-VALUE>
Script usage example:
    ./dm/dm_verify_node_services.sh wm CONFIG_MANAGER_WM
    ./dm/dm_verify_node_services.sh blem CONFIG_MANAGER_BLEM
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input arguments" -l "dm/dm_verify_node_services.sh" -arg
service=${1}
kconfig_val=${2}

trap '
fut_info_dump_line
print_tables Node_Services
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "dm/dm_verify_node_services.sh: DM test - Verify Node_Services table contains given service, respective enable field is set to true and is running"

check_kconfig_option "$kconfig_val" "y" &&
    log "dm/dm_verify_node_services.sh: $kconfig_val = y - KCONFIG exists on the device - Success" ||
    raise "FAIL: $kconfig_val - KCONFIG is not supported on the device" -l "dm/dm_verify_node_services.sh" -s

check_ovsdb_entry Node_Services -w service "$service" &&
    log "dm/dm_verify_node_services.sh: Node_Services table contains $service - Success" ||
    raise "FAIL: Node_Services table does not contain $service" -l "dm/dm_verify_node_services.sh" -tc

if [ $(get_ovsdb_entry_value Node_Services enable -w service $service) == "true" ]; then
    log "dm/dm_verify_node_services.sh: $service from Node_Services table that have enable field set to true"
    if [ -n $($(get_process_cmd) | grep /usr/opensync/bin/$service | grep -v 'grep' | wc -l) ]; then
        log "dm/dm_verify_node_services.sh: $service from Node_Services table is running - Success"
    else
        raise "FAIL: $service from Node_Services table is not running" -l "dm/dm_verify_node_services.sh" -tc
    fi
else
    raise "FAIL: $service from Node_Services table that have enable field not set to true"
fi

pass
