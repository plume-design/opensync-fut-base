#!/bin/sh
#!/bin/bhaul_mtu

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
othr/othr_verify_gre_tunnel_leaf.sh [-h] arguments
Description:
    - Script verifies GRE tunnel on LEAF device
Arguments:
    -h : show this help message
    \$1 (upstream_router_ip) : Router IP address to check        : (string)(optional) : (default:192.168.200.1)
    \$2 (internet_check_ip)  : Internet IP address to check      : (string)(optional) : (default:1.1.1.1)
    \$3 (n_ping)             : Number of ping packets            : (string)(optional) : (default:5)
Script usage example:
    ./othr/othr_verify_gre_tunnel_leaf.sh bhaul-sta-l50 br-home
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Inet_Config Wifi_Inet_State
print_tables Wifi_VIF_Config Wifi_VIF_State
print_tables DHCP_leased_IP
show_bridge_details
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM


# Input arguments common to GW and LEAF, optional:
upstream_router_ip=${1:-"192.168.200.1"}
internet_check_ip=${2:-"1.1.1.1"}
n_ping=${3:-"5"}

# LEAF validation step #2
# Enforce router connectivity, check-only internet connectivity
log "othr/othr_verify_gre_tunnel_leaf.sh: Check that LEAF has WAN connectivity via GRE tunnel"
wait_for_function_response 0 "ping -c${n_ping} ${upstream_router_ip}" &&
    log "othr/othr_verify_gre_tunnel_leaf.sh: Can ping router ${upstream_router_ip} - Success" ||
    raise "FAIL: Can not ping router ${upstream_router_ip}" -tc

wait_for_function_response 0 "ping -c${n_ping} ${internet_check_ip}" &&
    log "othr/othr_verify_gre_tunnel_leaf.sh: Can ping internet ${internet_check_ip} - Success" ||
    log -wrn "othr/othr_verify_gre_tunnel_leaf.sh: Can not ping internet ${internet_check_ip}"

pass
