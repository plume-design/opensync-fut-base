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
nm2/nm2_enable_disable_iface_network.sh [-h] arguments
Description:
    - Script enables and disables interface through Wifi_Inet_Config table
      Script fails if Wifi_Inet_State 'network' field does not match Wifi_Inet_Config
Arguments:
    -h  show this help message
    \$1 (if_name) : used as if_name in Wifi_Inet_Config table : (string)(required)
    \$2 (if_type) : used as if_type in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_enable_disable_iface_network.sh <IF-NAME> <IF-TYPE>
Script usage example:
    ./nm2/nm2_enable_disable_iface_network.sh eth0 eth
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_enable_disable_iface_network.sh" -arg
if_name=$1
if_type=$2
inet_addr=10.10.10.30

trap '
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    check_restore_management_access || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_enable_disable_iface_network.sh: NM2 test - Enable disable interface"

log "nm2/nm2_enable_disable_iface_network.sh: Creating Wifi_Inet_Config entries for: $if_name"
create_inet_entry \
    -if_name "$if_name" \
    -enabled true \
    -network true \
    -if_type "$if_type" \
    -ip_assign_scheme static \
    -netmask "255.255.255.0" \
    -inet_addr "$inet_addr" &&
        log "nm2/nm2_enable_disable_iface_network.sh: Interface $if_name created - Success" ||
        raise "FAIL: Failed to create $if_name interface" -l "nm2/nm2_enable_disable_iface_network.sh" -ds

if [ $FUT_SKIP_L2 != 'true' ]; then
    log "nm2/nm2_enable_disable_iface_network.sh: LEVEL2 - Check if IP address $inet_addr was properly applied to $if_name"
    wait_for_function_response 0 "check_interface_ip_address_set_on_system $if_name | grep -q \"$inet_addr\"" &&
        log "nm2/nm2_enable_disable_iface_network.sh: Setting applied to ifconfig - IP: $inet_addr - Success" ||
        raise "FAIL: Failed to apply settings to ifconfig - IP: $inet_addr" -l "nm2/nm2_enable_disable_iface_network.sh" -tc
fi

log "nm2/nm2_enable_disable_iface_network.sh: Disabling network, setting Wifi_Inet_Config::network to 'false'"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u network false &&
    log "nm2/nm2_enable_disable_iface_network.sh: update_ovsdb_entry - Wifi_Inet_Config::network is 'false' - Success" ||
    raise "FAIL: update_ovsdb_entry - Wifi_Inet_Config::network is not 'false'" -l "nm2/nm2_enable_disable_iface_network.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is network false &&
    log "nm2/nm2_enable_disable_iface_network.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::network is 'false' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::network is not 'false'" -l "nm2/nm2_enable_disable_iface_network.sh" -tc

if [ $FUT_SKIP_L2 != 'true' ]; then
    log "nm2/nm2_enable_disable_iface_network.sh: Checking if all network settings on interface are empty - LEVEL2"
    wait_for_function_response 1 "check_interface_ip_address_set_on_system $if_name | grep -q \"$inet_addr\"" &&
        log "nm2/nm2_enable_disable_iface_network.sh: Setting removed from ifconfig for '$if_name' - Success" ||
        raise "FAIL: Failed to remove settings from ifconfig for '$if_name'" -l "nm2/nm2_enable_disable_iface_network.sh" -tc
fi

log "nm2/nm2_enable_disable_iface_network.sh: Re-enabling network, setting Wifi_Inet_Config::network to 'true'"
update_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -u network true &&
    log "nm2/nm2_enable_disable_iface_network.sh: update_ovsdb_entry - Wifi_Inet_Config::network is 'true' - Success" ||
    raise "FAIL: update_ovsdb_entry - Wifi_Inet_Config::network is not 'true'" -l "nm2/nm2_enable_disable_iface_network.sh" -oe

wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is network true &&
    log "nm2/nm2_enable_disable_iface_network.sh: wait_ovsdb_entry - Wifi_Inet_Config reflected to Wifi_Inet_State::network is 'true' - Success" ||
    raise "FAIL: wait_ovsdb_entry - Failed to reflect Wifi_Inet_Config to Wifi_Inet_State::network is not 'true'" -l "nm2/nm2_enable_disable_iface_network.sh" -tc

if [ $FUT_SKIP_L2 != 'true' ]; then
    log "nm2/nm2_enable_disable_iface_network.sh: LEVEL2 - Check if IP address $inet_addr was properly applied to $if_name"
    wait_for_function_response 0 "check_interface_ip_address_set_on_system $if_name | grep -q \"$inet_addr\"" &&
        log "nm2/nm2_enable_disable_iface_network.sh: Setting applied to ifconfig - IP: $inet_addr - Success" ||
        raise "FAIL: Failed to apply settings to ifconfig - IP: $inet_addr" -l "nm2/nm2_enable_disable_iface_network.sh" -tc
fi

pass
