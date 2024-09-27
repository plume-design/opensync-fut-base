#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/dm_setup.sh"
status=""
usage()
{
cat << usage_string
dm/dm_verify_enable_node_services.sh [-h] arguments
Description:
    - Check if manager/service is running if 'enable' field in the 'Node_Services'
      table is set true.
    - Check if manager/service is killed if 'enable' field in the 'Node_Services'
      table is set false.
Arguments:
    -h  show this help message
    \$1 (manager)     : Node_Services::service to verify                 : (string)(required)
    \$2 (kconfig_val) : Kconfig option to check if 'manager' is compiled : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./dm/dm_verify_enable_node_services.sh <MANAGER> <KCONFIG_VAL>
Script usage example:
    ./dm/dm_verify_enable_node_services.sh wm CONFIG_MANAGER_WM
    ./dm/dm_verify_enable_node_services.sh blem CONFIG_MANAGER_BLEM
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input arguments" -l "dm/dm_verify_enable_node_services.sh" -arg
manager=${1}
kconfig_val=${2}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Node_Services
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "dm/dm_verify_enable_node_services.sh: DM test - Verify status of each manager against 'enable' field value in the 'Node_Services' table."

print_tables Node_Services

check_kconfig_option "$kconfig_val" "y" &&
    log "dm/dm_verify_enable_node_services.sh: $kconfig_val = y - KCONFIG exists on the device - Success" ||
    raise "$kconfig_val != y - KCONFIG does not exist on the device" -l "dm/dm_verify_enable_node_services.sh" -s

check_ovsdb_entry Node_Services -w service "$manager" &&
    log "dm/dm_verify_enable_node_services.sh: Node_Services table contains $manager - Success" ||
    raise "Node_Services table does not contain $manager" -l "dm/dm_verify_enable_node_services.sh" -tc

service_enabled=$(get_ovsdb_entry_value Node_Services enable -w service $manager -r)

wait_for_function_response "notempty" "get_pid ${OPENSYNC_ROOTDIR}/bin/${manager}" 10 &&
  pid_of_manager=$(get_pid "${OPENSYNC_ROOTDIR}/bin/$manager") ||
  pid_of_manager=""

log -deb "dm/dm_verify_enable_node_services.sh: PID is '${pid_of_manager}'"

if [ $service_enabled == "false" ]; then
    status="not "
    [ -z $pid_of_manager ] ||
        raise "Service ${manager} is running despite 'enable' field is set 'false' in 'Node_Services' table." -l "dm/dm_verify_enable_node_services.sh" -tc
elif [ $service_enabled == "true" ]; then
    [ -z $pid_of_manager ] &&
        raise "Service ${manager} is not running despite 'enable' field is set 'true' in 'Node_Services' table." -l "dm/dm_verify_enable_node_services.sh" -tc
else
    raise "'enable' field for ${manager} is set invalid value in 'Node_Services' table." -l "dm/dm_verify_enable_node_services.sh" -tc
fi

log "dm/dm_verify_enable_node_services.sh: Service '${manager}' is ${status}running as 'enable' field is set '${service_enabled}' in the 'Node_Services' table - Success"

pass

