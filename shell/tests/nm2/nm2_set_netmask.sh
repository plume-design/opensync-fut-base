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
nm2/nm2_set_netmask.sh [-h] arguments
Description:
    - Script configures interfaces netmask through Wifi_inet_Config 'netmask' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (if_name) : used as if_name in Wifi_Inet_Config table : (string)(required)
    \$2 (if_type) : used as if_type in Wifi_Inet_Config table : (string)(required)
    \$3 (netmask) : used as netmask in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_netmask.sh <IF-NAME> <IF-TYPE> <NETMASK>
Script usage example:
    ./nm2/nm2_set_netmask.sh eth0 eth 255.255.0.0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_netmask.sh" -arg
if_name=$1
if_type=$2
netmask=$3

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "nm2/nm2_set_netmask.sh: NM2 test - Testing table Wifi_Inet_Config field netmask - $netmask"

log "nm2/nm2_set_netmask.sh: Creating Wifi_Inet_Config entries for $if_name"
create_inet_entry \
    -if_name "$if_name" \
    -enabled true \
    -network true \
    -ip_assign_scheme static \
    -netmask 255.255.255.0 \
    -inet_addr 10.10.10.30 \
    -if_type "$if_type" &&
        log "nm2/nm2_set_netmask.sh: Interface $if_name created - Success" ||
        raise "Failed to create $if_name interface" -l "nm2/nm2_set_netmask.sh" -ds

log "nm2/nm2_set_netmask.sh: Setting NETMASK for $if_name to $netmask"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u netmask "$netmask" &&
    log "nm2/nm2_set_netmask.sh: update_ovsdb_entry - Wifi_Inet_Config table::netmask is $netmask - Success" ||
    raise "update_ovsdb_entry - Failed to update Wifi_Inet_Config::netmask is not $netmask" -l "nm2/nm2_set_netmask.sh" -fc

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is netmask "$netmask" &&
    log "nm2/nm2_set_netmask.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::netmask is $netmask - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::netmask is not $netmask" -l "nm2/nm2_set_netmask.sh" -tc

log "nm2/nm2_set_netmask.sh: Check if NETMASK was properly applied to $if_name - LEVEL2"
wait_for_function_response 0 "check_interface_netmask_set_on_system $if_name | grep -q \"$netmask\"" &&
    log "nm2/nm2_set_netmask.sh: LEVEL2 - NETMASK applied to ifconfig for interface $if_name - Success" ||
    raise "LEVEL2 - Failed to apply NETMASK to ifconfig for interface $if_name" -l "nm2/nm2_set_netmask.sh" -tc

pass
