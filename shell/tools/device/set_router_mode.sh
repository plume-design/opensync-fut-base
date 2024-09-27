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
tools/device/set_router_mode.sh [-h] arguments
Description:
    - Scripts sets device working mode into Router mode
Arguments:
    -h  show this help message
    - \$1 (i_if)        : Name of interface to set UPnP mode 'internal' : (string)(required)
    - \$2 (i_dhcpd)     : Internal interface dhcpd                      : (string)(required)
    - \$3 (i_inet_addr) : Internal interface inet_addr                  : (string)(required)
    - \$4 (e_if)        : Name of interface to set UPnP mode 'external' : (string)(required)
Script usage example:
    ./tools/device/set_router_mode.sh br-home home-ap-l50
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=4
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
internal_if_name=${1}
internal_dhcpd=${2}
internal_inet_addr=${3}
external_if_name=${4}

# Fixed args internal
internal_NAT=false
internal_ip_assign_scheme=static
internal_upnp_mode=internal
internal_network=true
internal_enabled=true
internal_netmask=255.255.255.0

# Fixed args external
external_NAT=true
external_ip_assign_scheme=dhcp
external_upnp_mode=external
external_network=true
external_enabled=true

log_title "tools/device/set_router_mode.sh: Putting device into router mode" ||
    log "tools/device/set_router_mode.sh: Removing bridge port ${external_if_name} from bridge ${internal_if_name} if present"
remove_port_from_bridge "${internal_if_name}" "${external_if_name}" &&
    log "tools/device/set_router_mode.sh: Bridge port removed or it did not existed in first place" ||
    raise "Removal of bridge port ${external_if_name} from bridge ${internal_if_name} - Failed" -l "tools/device/set_router_mode.sh" -tc

log "tools/device/set_router_mode.sh: Configuring internal interface - ${internal_if_name}"
create_inet_entry \
    -if_name "${internal_if_name}" \
    -dhcpd "${internal_dhcpd}" \
    -inet_addr "${internal_inet_addr}" \
    -netmask "${internal_netmask}" \
    -NAT "${internal_NAT}" \
    -ip_assign_scheme "${internal_ip_assign_scheme}" \
    -upnp_mode "${internal_upnp_mode}" \
    -network "${internal_network}" \
    -enabled "${internal_enabled}" &&
    log "tools/device/set_router_mode.sh: Internal interface ${internal_if_name} configured - Success" ||
    raise "Internal interface ${internal_if_name} configuration - Failed" -l "tools/device/set_router_mode.sh" -tc

log "tools/device/set_router_mode.sh: Configuring external interface - ${external_if_name}"
create_inet_entry \
    -if_name "${external_if_name}" \
    -NAT "${external_NAT}" \
    -ip_assign_scheme "${external_ip_assign_scheme}" \
    -upnp_mode "${external_upnp_mode}" \
    -network "${external_network}" \
    -enabled "${external_enabled}" &&
    log "tools/device/set_router_mode.sh: External interface ${external_if_name} configured - Success" ||
    raise "External interface ${external_if_name} configuration - Failed" -l "tools/device/set_router_mode.sh" -tc

log "tools/device/set_router_mode.sh: Device is in ROUTER mode - Success"
exit 0
