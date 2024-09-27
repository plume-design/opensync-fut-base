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
nm2/nm2_set_inet_addr.sh [-h] arguments
Description:
    - Script configures interfaces inet address through Wifi_inet_Config 'inet_addr' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (if_name)   : used as if_name in Wifi_Inet_Config table   : (string)(required)
    \$2 (if_type)   : used as if_type in Wifi_Inet_Config table   : (string)(required)
    \$3 (inet_addr) : used as inet_addr in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_inet_addr.sh <IF-NAME> <IF-TYPE> <INET-ADDR>
Script usage example:
    ./nm2/nm2_set_inet_addr.sh eth0 eth 10.0.0.35
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_inet_addr.sh" -arg
if_name=$1
if_type=$2
inet_addr=$3

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "nm2/nm2_set_inet_addr.sh: NM2 test - Testing table Wifi_Inet_Config field inet_addr"

log "nm2/nm2_set_inet_addr.sh: Creating Wifi_Inet_Config entries for $if_name (enabled=true, network=true, ip_assign_scheme=static)"
create_inet_entry \
    -if_name "$if_name" \
    -enabled true \
    -network true \
    -netmask "255.255.255.0" \
    -ip_assign_scheme static \
    -if_type "$if_type" \
    -inet_addr "$inet_addr" &&
        log "nm2/nm2_set_inet_addr.sh: Interface $if_name created - Success" ||
        raise "Failed to create $if_name interface" -l "nm2/nm2_set_inet_addr.sh" -ds

log "nm2/nm2_set_inet_addr.sh: Setting Wifi_Inet_Config::inet_addr to $inet_addr"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u inet_addr "$inet_addr" &&
    log "nm2/nm2_set_inet_addr.sh: update_ovsdb_entry - Wifi_Inet_Config::inet_addr is $inet_addr - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Inet_Config::inet_addr is not $inet_addr" -l "nm2/nm2_set_inet_addr.sh" -fc

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is inet_addr "$inet_addr" &&
    log "nm2/nm2_set_inet_addr.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::inet_addr is $inet_addr - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::inet_addr is not $inet_addr" -l "nm2/nm2_set_inet_addr.sh" -tc

log "nm2/nm2_set_inet_addr.sh: Checking if INET_ADDR was properly applied to $if_name - LEVEL2"
wait_for_function_response 0 "check_interface_ip_address_set_on_system $if_name | grep -q \"$inet_addr\"" &&
    log "nm2/nm2_set_inet_addr.sh: INET_ADDR applied to ifconfig - interface $if_name" ||
    raise "Failed to apply INET_ADDR to ifconfig - interface $if_name" -l "nm2/nm2_set_inet_addr.sh" -tc

log "nm2/nm2_set_inet_addr.sh: Removing INET_ADDR for $if_name"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u inet_addr "[\"set\",[]]" &&
    log "nm2/nm2_set_inet_addr.sh: update_ovsdb_entry - Wifi_Inet_Config::inet_addr is [\"set\",[]] - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Inet_Config::inet_addr is not [\"set\",[]]" -l "nm2/nm2_set_inet_addr.sh" -fc

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is inet_addr "0.0.0.0" &&
    log "nm2/nm2_set_inet_addr.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::inet_addr is '0.0.0.0' - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::inet_addr is not '0.0.0.0'" -l "nm2/nm2_set_inet_addr.sh" -tc

log "nm2/nm2_set_inet_addr.sh: Checking if INET_ADDR was properly removed for $if_name - LEVEL2"
wait_for_function_response 1 "check_interface_ip_address_set_on_system $if_name | grep -q \"$inet_addr\"" &&
    log "nm2/nm2_set_inet_addr.sh: INET_ADDR removed from ifconfig for interface $if_name - Success" ||
    raise "Failed to remove INET_ADDR from ifconfig for interface $if_name" -l "nm2/nm2_set_inet_addr.sh" -tc

pass
