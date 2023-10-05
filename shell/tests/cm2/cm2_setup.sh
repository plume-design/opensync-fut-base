#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
cm2/cm2_setup.sh [-h] arguments
Description:
    - Setup device for CM testing
Arguments:
    -h : show this help message
    \$1 (wan_eth_if_name)    : Uplink ethernet interface name : (string)(optional)
    \$2 (wan_bridge_if_name) : WAN bridge interface name      : (string)(optional)
Script usage example:
    ./cm2/cm2_setup.sh
    ./cm2/cm2_setup.sh eth0 br-wan true
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_CM" "y" ||
    raise "CONFIG_MANAGER_CM != y - CM not present on device" -l "cm2/cm2_setup.sh" -s

wan_eth_if_name=${1}
wan_bridge_if_name=${2}

device_init &&
    log -deb "cm2/cm2_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "cm2/cm2_setup.sh" -ds

start_openswitch &&
    log -deb "cm2/cm2_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "cm2/cm2_setup.sh" -ds

manipulate_iptables_protocol unblock DNS &&
    log -deb "cm2/cm2_setup.sh - iptables unblock DNS - Success" ||
    raise "FAIL: manipulate_iptables_protocol unblock DNS - Could not unblock DNS traffic" -l "cm2/cm2_setup.sh" -ds

manipulate_iptables_protocol unblock SSL &&
    log -deb "cm2/cm2_setup.sh - iptables unblock SSL - Success" ||
    raise "FAIL: Could not unblock SSL traffic: manipulate_iptables_protocol unblock SSL" -l "cm2/cm2_setup.sh" -ds

# Legacy procedure requires manual adding of WAN ethernet interface into WAN bridge
check_kconfig_option "CONFIG_MANAGER_WANO" "y" && is_wano=true || is_wano=false
if [ -n "${wan_eth_if_name}" ] && [ -n "${wan_bridge_if_name}" ] && [ $is_wano == false ] ; then
    add_interface_to_bridge "${wan_bridge_if_name}" "${wan_eth_if_name}" &&
        log -deb "cm2/cm2_setup.sh - Interface added to bridge - Success" ||
        raise "FAIL: add_interface_to_bridge $wan_bridge_if_name $wan_eth_if_name - Could not add interface to bridge" -l "cm2/cm2_setup.sh" -ds
else
    log -deb "cm2/cm2_setup.sh - Device does not require adding bridge interface"
    log -deb "Details:\nwan_eth_if_name: ${wan_eth_if_name}\nwan_bridge_if_name: ${wan_bridge_if_name}\nis_wano: ${is_wano}"
fi

restart_managers
log -deb "cm2/cm2_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "cm2/cm2_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty table:" -l "cm2/cm2_setup.sh" -ds

set_manager_log CM TRACE &&
    log -deb "cm2/cm2_setup.sh - Manager log for CM set to TRACE - Success" ||
    raise "FAIL: set_manager_log CM TRACE - Could not set manager log severity" -l "cm2/cm2_setup.sh" -ds

wait_for_function_response 0 "check_default_route_gw" &&
    log -deb "cm2/cm2_setup.sh - Default GW added to routes - Success" ||
    raise "FAIL: check_default_route_gw - Default GW not added to routes" -l "cm2/cm2_setup.sh" -ds
