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
nm2/nm2_vlan_interface.sh [-h] arguments
Description:
    - Script creates VLAN through Wifi_Inet_Config table and validates its existence in Wifi_Inet_State table and on the
      system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (parent_ifname)  : used as parent_ifname in Wifi_Inet_Config table           : (string)(required)
    \$2 (vlan_id)        : used as vlan_id for virtual interface '100' in 'eth0.100' : (integer)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_vlan_interface.sh <parent_ifname> <vlan_id>
Script usage example:
    ./nm2/nm2_vlan_interface.sh eth0 100
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_OSN_LINUX_VLAN" "y" &&
    log "nm2/nm2_vlan_interface.sh: CONFIG_OSN_LINUX_VLAN==y - VLAN is enabled on this device" ||
    raise "CONFIG_OSN_LINUX_VLAN != y - VLAN is disabled on this device" -l "nm2/nm2_vlan_interface.sh" -s

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_vlan_interface.sh" -arg
parent_ifname=$1
vlan_id=$2

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    delete_inet_interface "$if_name"
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

# Construct if_name from parent_ifname and vlan_id (example: eth0.100).
if_name="$parent_ifname.$vlan_id"

log_title "nm2/nm2_vlan_interface.sh: NM2 test - Testing vlan_id"

log "nm2/nm2_vlan_interface.sh: Creating Wifi_Inet_Config entry for $if_name (enabled=true, network=true, ip_assign_scheme=static)"
create_inet_entry \
    -if_name "$if_name" \
    -enabled true \
    -network true \
    -ip_assign_scheme static \
    -inet_addr "10.10.10.$vlan_id" \
    -netmask "255.255.255.0" \
    -if_type vlan \
    -vlan_id "$vlan_id" \
    -parent_ifname "$parent_ifname" &&
        log "nm2/nm2_vlan_interface.sh: Interface $if_name created - Success" ||
        raise "Failed to create $if_name interface" -l "nm2/nm2_vlan_interface.sh" -ds

log "nm2/nm2_vlan_interface.sh: Check is interface $if_name up - LEVEL2"
wait_for_function_response 0 "check_eth_interface_state_is_up $if_name" &&
    log "nm2/nm2_vlan_interface.sh: wait_for_function_response - Interface $if_name is UP - Success" ||
    raise "wait_for_function_response - Interface $if_name is DOWN" -l "nm2/nm2_vlan_interface.sh" -ds

log "nm2/nm2_vlan_interface.sh: Check if VLAN interface $if_name exists at OS level - LEVEL2"
check_vlan_iface "$parent_ifname" "$vlan_id" &&
    log "nm2/nm2_vlan_interface.sh: VLAN interface $if_name exists at OS level - Success" ||
    raise "VLAN interface $if_name does not exist at OS level" -l "nm2/nm2_vlan_interface.sh" -tc

log "nm2/nm2_vlan_interface.sh: Remove VLAN interface"
delete_inet_interface "$if_name" &&
    log "nm2/nm2_vlan_interface.sh: VLAN interface $if_name removed from device - Success" ||
    raise "VLAN interface $if_name not removed from device" -l "nm2/nm2_vlan_interface.sh" -tc

pass
