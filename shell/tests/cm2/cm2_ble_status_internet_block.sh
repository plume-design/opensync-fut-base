#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

cm_setup_file="cm2/cm2_setup.sh"
adr_internet_man_file="tools/server/cm/address_internet_man.sh"
step_1_name="internet_blocked"
step_1_bit_process="15"
step_2_name="internet_recovered"
step_2_bit_process="75"
usage()
{
cat << usage_string
cm2/cm2_ble_status_internet_block.sh [-h] arguments
Description:
    - Script observes AW_Bluetooth_Config table field 'payload' during internet reconnection
      If AW_Bluetooth_Config payload field fails to change in given sequence test fails
Arguments:
    -h : show this help message
    \$1 (test_step) : used as test step : (string)(required) : (${step_1_name}, ${step_2_name})
Testcase procedure:
    - On DEVICE: Run: ${cm_setup_file} (see ${cm_setup_file} -h)
                 Run: cm2/cm2_ble_status_internet_block.sh ${step_1_name}
    - On RPI SERVER: Run: ${adr_internet_man_file} <WAN-IP-ADDRESS> block
    - On DEVICE: Run: cm2/cm2_ble_status_internet_block.sh ${step_2_name}
    - On RPI SERVER: Run: ${adr_internet_man_file} <WAN-IP-ADDRESS> unblock
Script usage example:
    ./cm2/cm2_ble_status_internet_block.sh ${step_1_name}
    ./cm2/cm2_ble_status_internet_block.sh ${step_2_name}
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_BLEM" "y" ||
    raise "CONFIG_MANAGER_BLEM != y - BLE not present on device" -l "cm2/cm2_ble_status_internet_block.sh" -s

check_kconfig_option "TARGET_CAP_EXTENDER" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Testcase applicable only for EXTENDER-s" -l "cm2/cm2_ble_status_internet_block.sh" -s

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "cm2/cm2_ble_status_internet_block.sh" -arg
test_step=${1}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables AW_Bluetooth_Config
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "cm2/cm2_ble_status_internet_block.sh: CM2 test - Observe BLE Status - $test_step"

case $test_step in
    ${step_1_name})
        bit_process=${step_1_bit_process}
        for bit in $bit_process; do
            log "cm2/cm2_ble_status_internet_block.sh: Checking AW_Bluetooth_Config::payload for $bit:00:00:00:00:00"
            wait_ovsdb_entry AW_Bluetooth_Config -is payload "$bit:00:00:00:00:00" &&
                log "cm2/cm2_ble_status_internet_block.sh: wait_ovsdb_entry - AW_Bluetooth_Config::payload changed to $bit:00:00:00:00:00 - Success" ||
                raise "AW_Bluetooth_Config::payload failed to change to $bit:00:00:00:00:00" -l "cm2/cm2_ble_status_internet_block.sh" -tc
        done
    ;;
    ${step_2_name})
        bit_process=${step_2_bit_process}
        for bit in $bit_process; do
            log "cm2/cm2_ble_status_internet_block.sh: Checking AW_Bluetooth_Config::payload for $bit:00:00:00:00:00"
            wait_ovsdb_entry AW_Bluetooth_Config -is payload "$bit:00:00:00:00:00" &&
                log "cm2/cm2_ble_status_internet_block.sh: wait_ovsdb_entry - AW_Bluetooth_Config::payload changed to $bit:00:00:00:00:00 - Success" ||
                raise "AW_Bluetooth_Config::payload failed to change to $bit:00:00:00:00:00" -l "cm2/cm2_ble_status_internet_block.sh" -tc
        done
    ;;
    *)
        raise "Incorrect test_step provided" -l "cm2/cm2_ble_status_internet_block.sh" -arg
esac

pass
