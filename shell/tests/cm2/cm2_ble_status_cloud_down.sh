#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

cm_setup_file="cm2/cm2_setup.sh"
manipulate_port_num_file="tools/server/cm/manipulate_port_num.sh"
step_1_name="cloud_down"
step_1_bit_process="35"
step_2_name="cloud_recovered"
step_2_bit_process="75"
usage()
{
cat << usage_string
cm2/cm2_ble_status_cloud_down.sh [-h] arguments
Description:
    - Script checks if CM updates AW_Bluetooth_Config field 'payload' when Cloud is unreachable.
      If the field 'payload' does not reach expected value, test fails
Arguments:
    -h : show this help message
    \$1 (test_step)                 : used as test step                : (string)(optional) : (default:${step_1_name}) : (${step_1_name}, ${step_2_name})
Testcase procedure:
    - On DEVICE: Run: ${cm_setup_file} (see ${cm_setup_file} -h)
    - On DEVICE: Run: cm2/cm2_ble_status_cloud_down.sh ${step_1_name}
    - On RPI SERVER: Run: ${manipulate_port_num_file} <WAN-IP-ADDRESS> <PORT_NUM> block
    - On DEVICE: Run: cm2/cm2_ble_status_cloud_down.sh ${step_2_name}
    - On RPI SERVER: Run: ${manipulate_port_num_file} <WAN-IP-ADDRESS> <PORT_NUM> unblock
    - On DEVICE: Run: cm2/cm2_ble_status_cloud_down.sh ${step_1_name}
Script usage example:
    ./cm2/cm2_ble_status_cloud_down.sh ${step_1_name}
    ./cm2/cm2_ble_status_cloud_down.sh ${step_2_name}
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_BLEM" "y" ||
    raise "CONFIG_MANAGER_BLEM != y - BLE not present on device" -l "cm2/cm2_ble_status_cloud_down.sh" -s

check_kconfig_option "TARGET_CAP_EXTENDER" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Testcase applicable only for EXTENDER-s" -l "cm2/cm2_ble_status_cloud_down.sh" -s

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "cm2/cm2_ble_status_cloud_down.sh" -arg
one_sec=1000
test_step=${1}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Manager Connection_Manager_Uplink
    print_tables AW_Bluetooth_Config
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "cm2/cm2_ble_status_cloud_down.sh: CM2 test - Observe BLE Status payload - Cloud failure - $test_step"

print_tables AW_Bluetooth_Config

if [ "$test_step" = "${step_1_name}" ]; then
    # Setting Manager::inactivity_probe to speed up process
    inactivity_probe_store=$(get_ovsdb_entry_value Manager inactivity_probe)
    update_ovsdb_entry Manager -u inactivity_probe "$one_sec"
    # Verifying AW_Bluetooth_Config::payload
    bit_process=${step_1_bit_process}
    for bit in $bit_process; do
        log "cm2/cm2_ble_status_cloud_down.sh: Checking AW_Bluetooth_Config::payload for $bit:00:00:00:00:00"
        wait_ovsdb_entry AW_Bluetooth_Config -is payload "$bit:00:00:00:00:00" &&
            log "cm2/cm2_ble_status_cloud_down.sh: wait_ovsdb_entry - AW_Bluetooth_Config::payload changed to $bit:00:00:00:00:00 - Success" ||
            raise "AW_Bluetooth_Config::payload failed to change to $bit:00:00:00:00:00" -l "cm2/cm2_ble_status_cloud_down.sh" -tc
    done
    # Restoring Manager::inactivity_probe
    update_ovsdb_entry Manager -u inactivity_probe "$inactivity_probe_store"
elif [ "$test_step" = "${step_2_name}" ]; then
    bit_process=${step_2_bit_process}
    for bit in $bit_process; do
        log "cm2/cm2_ble_status_cloud_down.sh: Checking AW_Bluetooth_Config::payload for $bit:00:00:00:00:00"
        wait_ovsdb_entry AW_Bluetooth_Config -is payload "$bit:00:00:00:00:00" &&
            log "cm2/cm2_ble_status_cloud_down.sh: wait_ovsdb_entry - AW_Bluetooth_Config::payload changed to $bit:00:00:00:00:00 - Success" ||
            raise "AW_Bluetooth_Config::payload failed to change to $bit:00:00:00:00:00" -l "cm2/cm2_ble_status_cloud_down.sh" -tc
    done
else
    raise "Wrong test type option" -l "cm2/cm2_ble_status_cloud_down.sh" -arg
fi

pass
