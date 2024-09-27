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
nm2/nm2_set_broadcast.sh [-h] arguments
Description:
    - Script configures interfaces broadcast through Wifi_inet_Config 'broadcast' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (if_name)   : used as if_name in Wifi_Inet_Config table   : (string)(required)
    \$2 (if_type)   : used as if_type in Wifi_Inet_Config table   : (string)(required)
    \$3 (broadcast) : used as broadcast in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_broadcast.sh <IF-NAME> <IF-TYPE> <BROADCAST>
Script usage example:
    ./nm2/nm2_set_broadcast.sh wifi0 vif 10.0.0.10
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_broadcast.sh" -arg
if_name=$1
if_type=$2
broadcast=$3

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "nm2/nm2_set_broadcast.sh: NM2 test - Testing table Wifi_Inet_Config field broadcast"

log "nm2/nm2_set_broadcast.sh: Creating Wifi_Inet_Config entries for $if_name"
create_inet_entry \
    -if_name "$if_name" \
    -enabled true \
    -network true \
    -ip_assign_scheme static \
    -inet_addr 10.10.10.30 \
    -netmask "255.255.255.0" \
    -if_type "$if_type" &&
        log "nm2/nm2_set_broadcast.sh: Interface $if_name created - Success" ||
        raise "Failed to create $if_name interface" -l "nm2/nm2_set_broadcast.sh" -ds

log "nm2/nm2_set_broadcast.sh: Setting BROADCAST for $if_name to $broadcast"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u broadcast "$broadcast" &&
    log "nm2/nm2_set_broadcast.sh: update_ovsdb_entry - Wifi_Inet_Config::broadcast is '$broadcast' - Success" ||
    raise "update_ovsdb_entry - Wifi_Inet_Config::broadcast is not '$broadcast'" -l "nm2/nm2_set_broadcast.sh" -fc

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is broadcast "$broadcast" &&
    log "nm2/nm2_set_broadcast.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::broadcast is '$broadcast' - Success" ||
    raise "wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::broadcast is not '$broadcast'" -l "nm2/nm2_set_broadcast.sh" -tc

log "nm2/nm2_set_broadcast.sh: Check if BROADCAST was properly applied to $if_name - LEVEL2"
wait_for_function_response 0 "check_interface_broadcast_set_on_system $if_name | grep -q \"$broadcast\"" &&
    log "nm2/nm2_set_broadcast.sh: LEVEL2 - BROADCAST applied to ifconfig - broadcast is $broadcast - Success" ||
    raise "LEVEL2 - Failed to apply BROADCAST to ifconfig - broadcast is not $broadcast" -l "nm2/nm2_set_broadcast.sh" -tc

log "nm2/nm2_set_broadcast.sh: Removing broadcast from Wifi_Inet_Config for $if_name"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" \
    -u broadcast 0.0.0.0 \
    -u ip_assign_scheme none &&
        log "nm2/nm2_set_broadcast.sh: update_ovsdb_entry - Wifi_Inet_Config::broadcast is '0.0.0.0' - Success" ||
        raise "update_ovsdb_entry - Wifi_Inet_Config::broadcast is not '0.0.0.0'" -l "nm2/nm2_set_broadcast.sh" -fc

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" \
    -is broadcast 0.0.0.0 \
    -is ip_assign_scheme none &&
        log "nm2/nm2_set_broadcast.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::broadcast is '0.0.0.0' - Success" ||
        raise "wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::broadcast is not '0.0.0.0'" -l "nm2/nm2_set_broadcast.sh" -tc

log "nm2/nm2_set_broadcast.sh: Checking if BROADCAST was properly removed for $if_name - LEVEL2"
wait_for_function_response 1 "check_interface_broadcast_set_on_system $if_name | grep -q \"$broadcast\"" &&
    log "nm2/nm2_set_broadcast.sh: LEVEL2 - BROADCAST removed from ifconfig for interface $if_name - Success" ||
    raise "LEVEL2 - Failed to remove BROADCAST from ifconfig for interface $if_name" -l "nm2/nm2_set_broadcast.sh" -tc

pass
