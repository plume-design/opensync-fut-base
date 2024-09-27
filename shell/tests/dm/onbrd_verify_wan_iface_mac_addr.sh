#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_wan_iface_mac_addr.sh [-h] arguments
Description:
    - Verify if WAN interface in Wifi_Inet_State has MAC address matching the system.
      If script is used without parameter it is for for WANO enabled devices and would
      determine the WAN interface name by itself by looking into Connection_Manager_Uplink table.
      If used with the parameter it is for no WANO enabled devices and it uses the
      provided parameter.
Arguments:
    -h  show this help message
    \$1 (if_name) : used as WAN interface name to check : (string)(optional)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_wan_iface_mac_addr.sh
    or (no WANO)
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_wan_iface_mac_addr.sh [<WAN_IF_NAME>]
Script usage example:
    ./onbrd/onbrd_verify_wan_iface_mac_addr.sh
    ./onbrd/onbrd_verify_wan_iface_mac_addr.sh eth0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    get_radio_mac_from_system "$wan_if_name"
    print_tables Connection_Manager_Uplink Wifi_Inet_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "onbrd/onbrd_verify_wan_iface_mac_addr.sh: ONBRD test - Verify if WAN interface in Wifi_Inet_State has MAC address matching the system"

NARGS=1
get_wan_ifname_max_retries=5
if [ $# -eq 0 ]; then
    print_tables Connection_Manager_Uplink
    for i in $(seq $get_wan_ifname_max_retries); do
        wan_if_name=$(get_wan_uplink_interface_name)
        if [ -n "$wan_if_name" ]; then
            break
        elif [ "$i" -eq $get_wan_ifname_max_retries ]; then
            raise "Could not auto-determine WAN interface from Connection_Manager_Uplink" -l "onbrd/onbrd_verify_wan_iface_mac_addr.sh" -tc
        fi

        log "onbrd/onbrd_verify_wan_iface_mac_addr.sh: Could not auto-determine WAN interface from Connection_Manager_Uplink, retrying in 3 seconds"
        sleep 3
    done
elif [ $# -eq ${NARGS} ]; then
    wan_if_name=${1}
elif [ $# -gt ${NARGS} ]; then
    usage
    raise "Requires at most ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_wan_iface_mac_addr.sh" -arg
fi

# shellcheck disable=SC2060
mac_address=$(get_radio_mac_from_system "$wan_if_name" | tr [A-Z] [a-z])
if [ -z "$mac_address" ]; then
    raise "Could not determine MAC for WAN interface '$wan_if_name' from system" -l "onbrd/onbrd_verify_wan_iface_mac_addr.sh" -tc
fi

log "onbrd/onbrd_verify_wan_iface_mac_addr.sh: Verify used WAN interface '$wan_if_name' MAC address equals '$mac_address'"
wait_ovsdb_entry Wifi_Inet_State -w if_name "$wan_if_name" -is hwaddr "$mac_address" &&
    log "onbrd/onbrd_verify_wan_iface_mac_addr.sh: wait_ovsdb_entry - Wifi_Inet_State '$wan_if_name' hwaddr is equal to '$mac_address' - Success" ||
    raise "wait_ovsdb_entry - Wifi_Inet_State '$wan_if_name' hwaddr is NOT equal to '$mac_address'" -l "onbrd/onbrd_verify_wan_iface_mac_addr.sh" -tc

pass
