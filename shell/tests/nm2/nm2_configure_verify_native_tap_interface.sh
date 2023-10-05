#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

tc_name="nm2/nm2_configure_verify_native_tap_interface.sh"
manager_setup_file="nm2/nm2_setup.sh"
usage()
{
cat << usage_string
nm2/nm2_configure_verify_native_tap_interface.sh [-h] arguments
Description:
    - The script creates the interface of the specified type by configuring
      the Wifi_Inet_Config table.
      It then validates that the entry is created for the interface in the
      Wifi_Inet_State table. Also, it verifies that the interface exists on
      the device (LEVEL2 check).
Arguments:
    -h  show this help message
    \$1 (if_name) : used as if_name in Wifi_Inet_Config table : (string)(required)
    \$2 (if_type) : used as if_type in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_configure_verify_native_tap_interface.sh <IF-NAME> <IF-TYPE>
Script usage example:
    ./nm2/nm2_configure_verify_native_tap_interface.sh eth0 tap
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "$tc_name" -arg
if_name=$1
if_type=$2

trap '
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    run_setup_if_crashed nm || true
    check_restore_management_access || true
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "$tc_name: Testing Interface creation - $if_name type $if_type"

log "$tc_name: creating Wifi_Inet_Config entry for $if_name"
insert_ovsdb_entry Wifi_Inet_Config \
    -i if_name "$if_name" \
    -i if_type "$if_type" \
    -i enabled true \
    -i network true \
    -i NAT false \
    -i ip_assign_scheme "none" \
    -i inet_addr "" \
    -i netmask "" \
    -i gateway "" \
    -i broadcast "" \
    -i ip_assign_scheme none \
    -i no_flood true &&
        log "$tc_name: creating Wifi_Inet_Config entry for $if_name - Success" ||
        raise "FAIL: creating Wifi_Inet_Config entry for $if_name" -l "$tc_name" -oe

log "$tc_name: validating if interface $if_name is present in Wifi_Inet_State table"
# Interface must be present in Wifi_Inet_State table.
wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is if_type "$if_type" &&
    log "$tc_name: validating if interface $if_name is present Wifi_Inet_State table - Success" ||
    raise "FAIL: validating interface present, $if_name not present" -l "$tc_name" -ow

log "$tc_name: validating if interface $if_name is configured on the device"
wait_for_function_response 0 "check_interface_exists $if_name" &&
    log "$tc_name: validating if interface $if_name is configured on the device - Success" ||
    raise "FAIL: LEVEL2 - interface $if_name is not configured on the device" -l "$tc_name" -tc

# Check if manager survived.
log "$tc_name: checking if nm is running"
manager_pid_file="${OPENSYNC_ROOTDIR}/bin/nm"
wait_for_function_response 0 "check_manager_alive $manager_pid_file" &&
    log "$tc_name: checking if nm is running - Success" ||
    raise "FAIL: nm is not running" -l "$tc_name" -tc

log "$tc_name: removing interface $if_name"
delete_inet_interface "$if_name" &&
    log "$tc_name: removing interface $if_name - Success" ||
    raise "FAIL:  removing interface $if_name failed" -l "$tc_name" -tc

log "$tc_name: checking if $if_name is removed from the device"
check_interface_exists "$if_name"
# returns 0 if the interface exists
if [ "$?" -eq 0 ]; then
    log "$tc_name: Failed to remove $if_name from the device - Fail"
    raise "FAIL: Interface $if_name of type $if_type exists on system, but should NOT" -l "$tc_name" -tc
fi

pass
