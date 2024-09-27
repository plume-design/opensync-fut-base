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
    cat <<usage_string
tools/device/set_bridge_mode.sh [-h] arguments
Description:
    - Scripts sets device working mode into Bridge mode
Arguments:
    -h  show this help message
    - \$1 (lan_bridge)  : Name of the LAN bridge interface : (string)(required)
    - \$2 (wan_if_name) : Primary WAN interface name       : (string)(required)
Script usage example:
    ./tools/device/set_bridge_mode.sh br-home eth0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
bridge_if_name=${1}
wan_if_name=${2}

# Fixed args internal
bridge_NAT=false
bridge_ip_assign_scheme=dhcp
bridge_upnp_mode=disabled
bridge_network=true
bridge_enabled=true
bridge_dhcpd="[\"map\",[]]"

# Fixed args WAN interface
wan_NAT=false
wan_ip_assign_scheme=none
wan_upnp_mode=disabled
wan_network=true
wan_enabled=true
wan_netmask=0.0.0.0
wan_inet_addr=0.0.0.0
wan_dhcpd="[\"map\",[]]"

log_title "tools/device/set_bridge_mode.sh: Putting device into router mode" ||
    log "tools/device/set_bridge_mode.sh: Configuring WAN interface - ${wan_if_name}"
create_inet_entry \
    -if_name "${wan_if_name}" \
    -NAT "${wan_NAT}" \
    -ip_assign_scheme "${wan_ip_assign_scheme}" \
    -upnp_mode "${wan_upnp_mode}" \
    -network "${wan_network}" \
    -enabled "${wan_enabled}" \
    -netmask "${wan_netmask}" \
    -inet_addr "${wan_inet_addr}" \
    -dhcpd "${wan_dhcpd}" &&
    log "tools/device/set_bridge_mode.sh: WAN interface ${wan_if_name} configured - Success" ||
    raise "WAN interface ${wan_if_name} configuration - Failed" -l "tools/device/set_bridge_mode.sh" -tc

log "tools/device/set_bridge_mode.sh: Adding bridge port ${wan_if_name} to ${bridge_if_name}"
add_port_to_bridge "$bridge_if_name" "$wan_if_name" &&
    log "tools/device/set_bridge_mode.sh: Bridge port ${wan_if_name} added to bridge ${bridge_if_name} - Success" ||
    raise "Adding of bridge port ${wan_if_name} to bridge ${bridge_if_name} - Failed" -l "tools/device/set_bridge_mode.sh" -tc

log "tools/device/set_bridge_mode.sh: Configuring Bridge interface - ${bridge_if_name}"
create_inet_entry \
    -if_name "${bridge_if_name}" \
    -NAT "${bridge_NAT}" \
    -ip_assign_scheme "${bridge_ip_assign_scheme}" \
    -upnp_mode "${bridge_upnp_mode}" \
    -network "${bridge_network}" \
    -dhcpd "${bridge_dhcpd}" \
    -enabled "${bridge_enabled}" &&
    log "tools/device/set_bridge_mode.sh: Bridge interface ${bridge_if_name} configured - Success" ||
    raise "Bridge interface ${bridge_if_name} configuration - Failed" -l "tools/device/set_bridge_mode.sh" -tc

sleep 5

log "tools/device/set_bridge_mode.sh: Disable DHCP on - ${wan_if_name}"
create_inet_entry \
    -if_name "${wan_if_name}" \
    -ip_assign_scheme "${wan_ip_assign_scheme}" &&
    log "tools/device/set_bridge_mode.sh: WAN ${wan_if_name} DHCP disabled - Success" ||
    raise "Failed to disable DHCP on ${wan_if_name} - Failed" -l "tools/device/set_bridge_mode.sh" -tc

log "tools/device/set_bridge_mode.sh: Device is in BRIDGE mode - Success"
exit 0
