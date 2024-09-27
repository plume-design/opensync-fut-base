#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm
usage()
{
cat << usage_string
othr/othr_verify_gre_tunnel_gw_cleanup.sh [-h] arguments
Description:
    - Script removes GRE interfaces from Wifi_Inet_Config and removes GRE interfaces from lan_bridge on DUT device
Arguments:
    -h : show this help message
    \$1 (lan_bridge) : used for LAN bridge name : (string)(required)
Script usage example:
    ./othr/othr_verify_gre_tunnel_gw_cleanup.sh br-home
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Inet_Config
    show_bridge_details
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_verify_gre_tunnel_gw_cleanup.sh" -arg
lan_bridge=${1}

gre_inet_interfaces=$(get_ovsdb_entry_value Wifi_Inet_Config if_name -w if_type gre -r)
log "othr/othr_verify_gre_tunnel_gw_cleanup.sh: GRE interfaces: "${gre_inet_interfaces}
for if_name in ${gre_inet_interfaces}; do
    remove_ovsdb_entry Wifi_Inet_Config -w if_name "${if_name}"
    remove_port_from_bridge "${lan_bridge}" "${if_name}"
done

pass
