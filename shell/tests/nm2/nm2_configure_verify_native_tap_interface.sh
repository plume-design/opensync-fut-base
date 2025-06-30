#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

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
Script usage example:
    ./nm2/nm2_configure_verify_native_tap_interface.sh <IF-NAME> <IF-TYPE>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_configure_verify_native_tap_interface.sh" -arg
if_name=$1
if_type=$2

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    run_setup_if_crashed nm || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "nm2/nm2_configure_verify_native_tap_interface.sh: Testing Interface creation - $if_name type $if_type"

log "nm2/nm2_configure_verify_native_tap_interface.sh: creating Wifi_Inet_Config entry for $if_name"
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
        log "nm2/nm2_configure_verify_native_tap_interface.sh: creating Wifi_Inet_Config entry for $if_name - Success" ||
        raise "creating Wifi_Inet_Config entry for $if_name" -l "nm2/nm2_configure_verify_native_tap_interface.sh" -fc

log "nm2/nm2_configure_verify_native_tap_interface.sh: validating if interface $if_name is present in Wifi_Inet_State table"
# Interface must be present in Wifi_Inet_State table.
wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is if_type "$if_type" &&
    log "nm2/nm2_configure_verify_native_tap_interface.sh: validating if interface $if_name is present Wifi_Inet_State table - Success" ||
    raise "validating interface present, $if_name not present" -l "nm2/nm2_configure_verify_native_tap_interface.sh" -fc

log "nm2/nm2_configure_verify_native_tap_interface.sh: validating if interface $if_name is configured on the device"
wait_for_function_response 0 "check_interface_exists $if_name" &&
    log "nm2/nm2_configure_verify_native_tap_interface.sh: validating if interface $if_name is configured on the device - Success" ||
    raise "LEVEL2 - interface $if_name is not configured on the device" -l "nm2/nm2_configure_verify_native_tap_interface.sh" -tc

log "nm2/nm2_configure_verify_native_tap_interface.sh: removing interface $if_name"
delete_inet_interface "$if_name" &&
    log "nm2/nm2_configure_verify_native_tap_interface.sh: removing interface $if_name - Success" ||
    raise " removing interface $if_name failed" -l "nm2/nm2_configure_verify_native_tap_interface.sh" -tc

log "nm2/nm2_configure_verify_native_tap_interface.sh: checking if $if_name is removed from the device"
check_interface_exists "$if_name" &&
    raise "Interface $if_name of type $if_type exists on system, but should NOT" -l "nm2/nm2_configure_verify_native_tap_interface.sh" -tc

pass
