#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

cm_setup_file="cm2/cm2_setup.sh"
iface_down_bits=01
iface_up_bits=75
default_if_name="eth0"
default_if_type="eth"
usage()
{
cat << usage_string
cm2/cm2_ble_status_interface_down.sh [-h] arguments
Description:
    - Script observes AW_Bluetooth_Config table field 'payload' during drop/up of link interface.
      If AW_Bluetooth_Config payload field fails to change in given sequence (${if_down_up_process_bits}), test fails
Arguments:
    -h : show this help message
    \$1 (if_name) : interface name : (string)(optional) : (default:${default_if_name})
    \$2 (if_type) : interface type : (string)(optional) : (default:${default_if_type})
Testcase procedure:
    - On DEVICE: Run: ${cm_setup_file} (see ${cm_setup_file} -h)
                 Run: cm2/cm2_ble_status_interface_down.sh <WAN-IF-NAME>
Script usage example:
    ./cm2/cm2_ble_status_interface_down.sh ${default_if_name}
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_BLEM" "y" ||
    raise "CONFIG_MANAGER_BLEM != y - BLE not present on device" -l "cm2/cm2_ble_status_interface_down.sh" -s

check_kconfig_option "TARGET_CAP_EXTENDER" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Testcase applicable only for EXTENDER-s" -l "cm2/cm2_ble_status_interface_down.sh" -s

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "cm2/cm2_ble_status_interface_down.sh" -arg
if_name=${1:-${default_if_name}}
if_type=${2:-${default_if_type}}

trap '
fut_info_dump_line
print_tables AW_Bluetooth_Config
ifconfig $if_name up || true
check_restore_management_access || true
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "cm2/cm2_ble_status_interface_down.sh: CM2 test - Observe BLE Status - Interface '${if_name}' down/up"

print_tables Manager

is_connected=$(${OVSH} s Manager is_connected -r)
if [ $is_connected = 'true' ]; then
    log "cm2/cm2_ble_status_interface_down.sh: Manager::is_connected indicates connection to Cloud is established"
else
    log "cm2/cm2_ble_status_interface_down.sh: Manager::is_connected indicates connection to Cloud is not established"
fi

log "cm2/cm2_ble_status_interface_down.sh: Simulating CM full reconnection by toggling interface"
log "cm2/cm2_ble_status_interface_down.sh: Dropping interface $if_name"
ifconfig "$if_name" down &&
    log "cm2/cm2_ble_status_interface_down.sh: Interface $if_name is down - Success" ||
    raise "FAIL: Could not bring down interface $if_name" -l "cm2/cm2_ble_status_interface_down.sh" -ds

wait_ovsdb_entry AW_Bluetooth_Config -is payload "$iface_down_bits:00:00:00:00:00" &&
    log "cm2/cm2_ble_status_interface_down.sh: wait_ovsdb_entry - AW_Bluetooth_Config::payload changed to $iface_down_bits:00:00:00:00:00" ||
    raise "FAIL: AW_Bluetooth_Config::payload failed to change to $iface_down_bits:00:00:00:00:00" -l "cm2/cm2_ble_status_interface_down.sh" -tc

log "cm2/cm2_ble_status_interface_down.sh: Bringing back interface $if_name"
ifconfig "$if_name" up &&
    log "cm2/cm2_ble_status_interface_down.sh: Interface $if_name is up - Success" ||
    raise "FAIL: Could not bring up interface $if_name" -l "cm2/cm2_ble_status_interface_down.sh" -ds

get_if_fn_type="check_${if_type}_interface_state_is_up"
wait_for_function_response 0 "$get_if_fn_type $if_name " &&
    log "cm2/cm2_ble_status_interface_down.sh: Interface $if_name is UP - Success" ||
    raise "FAIL: Interface $if_name is DOWN, should be UP" -l "cm2/cm2_ble_status_interface_down.sh" -ds

log "cm2/cm2_ble_status_interface_down.sh: Checking AW_Bluetooth_Config::payload for $iface_up_bits:00:00:00:00:00"
wait_ovsdb_entry AW_Bluetooth_Config -is payload "$iface_up_bits:00:00:00:00:00" &&
    log "cm2/cm2_ble_status_interface_down.sh: wait_ovsdb_entry - AW_Bluetooth_Config::payload changed to $iface_up_bits:00:00:00:00:00 - Success" ||
    raise "FAIL: AW_Bluetooth_Config::payload failed to change to $iface_up_bits:00:00:00:00:00" -l "cm2/cm2_ble_status_interface_down.sh" -tc

pass
