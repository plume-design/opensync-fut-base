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
nm2/nm2_configure_nonexistent_iface.sh [-h] arguments
Description:
    - Script creates undefined interface through Wifi_Inet_Config table
      Script fails if:
        - Undefined interface is not present in Wifi_Inet_State
        - Undefined interface is present on system
        - NM crashes during creation of undefined interface
Arguments:
    -h  show this help message
    \$1 (if_name)   : used as if_name in Wifi_Inet_Config table   : (string)(required)
    \$2 (if_type)   : used as if_type in Wifi_Inet_Config table   : (string)(required)
    \$3 (inet_addr) : used as inet_addr in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_configure_nonexistent_iface.sh <IF-NAME> <IF-TYPE> <INET-ADDR>
Script usage example:
    ./nm2/nm2_configure_nonexistent_iface.sh test1 eth 10.10.10.15
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_configure_nonexistent_iface.sh" -arg
if_name=$1
if_type=$2
ip_address=$3

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "nm2/nm2_configure_nonexistent_iface.sh: NM2 test - Configure non-existent interface"

log "nm2/nm2_configure_nonexistent_iface.sh: Creating NONEXISTENT interface $if_name of type $if_type"
insert_ovsdb_entry Wifi_Inet_Config \
    -i if_name "$if_name" \
    -i if_type "$if_type" \
    -i enabled true \
    -i network true \
    -i NAT false \
    -i inet_addr "$ip_address" \
    -i netmask "255.255.255.0" \
    -i broadcast "10.10.10.255" \
    -i ip_assign_scheme static \
    -i parent_ifname eth1 \
    -i mtu 1500 &&
        log "nm2/nm2_configure_nonexistent_iface.sh: NONEXISTENT interface $if_name created - Success" ||
        raise "Failed to insert_ovsdb_entry for $if_name" -l "nm2/nm2_configure_nonexistent_iface.sh" -fc

log "nm2/nm2_configure_nonexistent_iface.sh: Checking if NONEXISTENT interface $if_name was created"
# Interface must be present in Wifi_Inet_State table...
wait_ovsdb_entry Wifi_Inet_State -w if_name "$if_name" -is if_type "$if_type" &&
    log "nm2/nm2_configure_nonexistent_iface.sh: NONEXISTENT interface present in Wifi_Inet_State::if_name = $if_name - Success" ||
    raise "Wifi_Inet_State::if_name = $if_name not present" -l "nm2/nm2_configure_nonexistent_iface.sh" -fc

# ...but not on system.
wait_for_function_response 1 "check_interface_exists $if_name" &&
    log "nm2/nm2_configure_nonexistent_iface.sh: Interface $if_name of type $if_type does not exist on system - Success" ||
    raise "Interface $if_name of type $if_type exists on system, but should NOT" -l "nm2/nm2_configure_nonexistent_iface.sh" -tc

pass
