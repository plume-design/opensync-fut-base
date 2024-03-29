#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="nm2/nm2_setup.sh"
usage()
{
cat << usage_string
nm2/nm2_set_mtu.sh [-h] arguments
Description:
    - Script configures interfaces mtu through Wifi_inet_Config 'mtu' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (if_name) : used as if_name in Wifi_Inet_Config table : (string)(required)
    \$2 (if_type) : used as if_type in Wifi_Inet_Config table : (string)(required)
    \$3 (mtu)     : used as mtu in Wifi_Inet_Config table     : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_mtu.sh <IF-NAME> <IF-TYPE> <MTU>
Script usage example:
    ./nm2/nm2_set_mtu.sh eth0 eth 1500
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_mtu.sh" -arg
if_name=$1
if_type=$2
mtu=$3

trap '
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    check_restore_management_access || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_set_mtu.sh: NM2 test - Testing table Wifi_Inet_Config field mtu - $mtu"

log "nm2/nm2_set_mtu.sh: Creating Wifi_Inet_Config entries for $if_name (enabled=true, network=true, ip_assign_scheme=static)"
if [ "${if_type}" == "vif" ]; then
    create_inet_entry \
        -if_name "$if_name" \
        -enabled true \
        -network true \
        -ip_assign_scheme static \
        -if_type "$if_type" \
        -inet_addr "10.10.10.30" \
        -netmask "255.255.255.0" &&
            log "nm2/nm2_set_mtu.sh: Interface $if_name created - Success" ||
            raise "FAIL: Failed to create $if_name interface" -l "nm2/nm2_set_mtu.sh" -ds
else
    create_inet_entry \
        -if_name "$if_name" \
        -enabled true \
        -network true \
        -ip_assign_scheme static \
        -if_type "$if_type" \
        -inet_addr "10.10.10.30" \
        -netmask "255.255.255.0" &&
            log "nm2/nm2_set_mtu.sh: Interface $if_name created - Success" ||
            raise "FAIL: Failed to create $if_name interface" -l "nm2/nm2_set_mtu.sh" -ds
fi

log "nm2/nm2_set_mtu.sh: Setting MTU to $mtu"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u mtu "$mtu" &&
    log "nm2/nm2_set_mtu.sh: update_ovsdb_entry - Wifi_Inet_Config::mtu is $mtu - Success" ||
    raise "FAIL: update_ovsdb_entry - Wifi_Inet_Config::mtu is not $mtu" -l "nm2/nm2_set_mtu.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is mtu "$mtu" &&
    log "nm2/nm2_set_mtu.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::mtu is $mtu - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::mtu is not $mtu" -l "nm2/nm2_set_mtu.sh" -tc

log "nm2/nm2_set_mtu.sh: Checking if MTU was properly applied for $if_name - LEVEL2"
wait_for_function_response 0 "check_interface_mtu_set_on_system $if_name | grep -q \"$mtu\"" &&
    log "nm2/nm2_set_mtu.sh: LEVEL2 - MTU applied to ifconfig for interface $if_name - Success" ||
    raise "FAIL: LEVEL2 - Failed to apply MTU to ifconfig for interface $if_name" -l "nm2/nm2_set_mtu.sh" -tc

pass
