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
nm2/nm2_set_nat.sh [-h] arguments
Description:
    - Script configures interfaces NAT through Wifi_inet_Config 'NAT' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (if_name) : used as if_name in Wifi_Inet_Config table : (string)(required)
    \$2 (if_type) : used as if_type in Wifi_Inet_Config table : (string)(required)
    \$3 (NAT)     : used as NAT in Wifi_Inet_Config table     : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_nat.sh
Script usage example:
    ./nm2/nm2_set_nat.sh eth0 eth true
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_nat.sh" -arg
if_name=$1
if_type=$2
NAT=$3

trap '
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    check_restore_management_access || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_set_nat.sh: NM2 test - Testing table Wifi_Inet_Config field NAT - $NAT"

log "nm2/nm2_set_nat.sh: Creating Wifi_Inet_Config entry for $if_name (enabled=true, network=true, ip_assign_scheme=static)"
if [ "${if_type}" == "vif" ]; then
    create_inet_entry \
        -if_name "$if_name" \
        -enabled true \
        -network true \
        -ip_assign_scheme static \
        -if_type "$if_type" \
        -inet_addr "10.10.10.30" \
        -netmask "255.255.255.0" &&
            log "nm2/nm2_set_nat.sh: Interface $if_name created - Success" ||
            raise "FAIL: Failed to create $if_name interface" -l "nm2/nm2_set_nat.sh" -ds
else
    create_inet_entry \
        -if_name "$if_name" \
        -enabled true \
        -network true \
        -ip_assign_scheme static \
        -if_type "$if_type" &&
            log "nm2/nm2_set_nat.sh: Interface $if_name created - Success" ||
            raise "FAIL: Failed to create $if_name interface" -l "nm2/nm2_set_nat.sh" -ds
fi

log "nm2/nm2_set_nat.sh: Setting NAT for interface $if_name to $NAT"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u NAT "$NAT" &&
    log "nm2/nm2_set_nat.sh: update_ovsdb_entry - Wifi_Inet_Config::NAT is $NAT - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::NAT is not $NAT" -l "nm2/nm2_set_nat.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is NAT "$NAT" &&
    log "nm2/nm2_set_nat.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::NAT is $NAT - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::NAT is not $NAT" -l "nm2/nm2_set_nat.sh" -tc

if [ $FUT_SKIP_L2 != 'true' ]; then
    log "nm2/nm2_set_nat.sh: Checking state of NAT for $if_name (must be ON) - LEVEL2"
    wait_for_function_response 0 "check_interface_nat_enabled $if_name" &&
        log "nm2/nm2_set_nat.sh: LEVEL2 - NAT applied to iptables for interface $if_name - Success" ||
        raise "FAIL: LEVEL2 - Failed to apply NAT to iptables for interface $if_name" -l "nm2/nm2_set_nat.sh" -tc
fi

log "nm2/nm2_set_nat.sh: Disabling NAT for $if_name"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u NAT false &&
    log "nm2/nm2_set_nat.sh: update_ovsdb_entry - Wifi_Inet_Config table::NAT is 'false' - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to update Wifi_Inet_Config::NAT is not 'false'" -l "nm2/nm2_set_nat.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is NAT false &&
    log "nm2/nm2_set_nat.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::NAT is 'false' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::NAT is not 'false'" -l "nm2/nm2_set_nat.sh" -tc

if [ $FUT_SKIP_L2 != 'true' ]; then
    log "nm2/nm2_set_nat.sh: Checking state of NAT for $if_name (must be OFF) - LEVEL2"
    wait_for_function_response 1 "check_interface_nat_enabled $if_name" &&
        log "nm2/nm2_set_nat.sh: LEVEL2 - NAT removed from iptables for interface $if_name - Success" ||
        raise "FAIL: LEVEL2 - Failed to remove NAT from iptables for interface $if_name" -l "nm2/nm2_set_nat.sh" -tc
fi

pass
