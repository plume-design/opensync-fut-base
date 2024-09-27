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
tools/device/remove_tap_interfaces.sh [-h] arguments
Description:
    - Script removes all required TAP interfaces for home bridge
    - Bridges that will be configured:
        - <LAN-BRIDGE>.mdns
        - <LAN-BRIDGE>.ndp
        - <LAN-BRIDGE>.dns
        - <LAN-BRIDGE>.dpi
        - <LAN-BRIDGE>.upnp
        - <LAN-BRIDGE>.l2uf
        - <LAN-BRIDGE>.tx
        - <LAN-BRIDGE>.dhcp
        - <LAN-BRIDGE>.http
Arguments:
    -h  show this help message
    - \$1 (lan_bridge) : Name of LAN bridge interface : (string)(required)
Script usage example:
    ./tools/device/remove_tap_interfaces.sh br-home
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
lan_bridge_if_name=${1}

tap_interface_list="mdns ndp dns dpi upnp l2uf tx dhcp http devdpi"

for tap_name in $tap_interface_list; do
    tap_if_name="${lan_bridge_if_name}.${tap_name}"
    remove_port_from_bridge "${lan_bridge_if_name}" "${tap_if_name}" &&
        log "tools/device/remove_tap_interfaces.sh: TAP port ${tap_if_name} removed - Success" ||
        log -err "tools/device/remove_tap_interfaces.sh:  TAP port ${tap_if_name} remove - Failed"
    remove_ovsdb_entry Wifi_Inet_Config \
        -w if_name "${tap_if_name}" &&
        log "tools/device/remove_tap_interfaces.sh: TAP interface ${tap_if_name} removed - Success" ||
        log -err "tools/device/remove_tap_interfaces.sh:  TAP interface ${tap_if_name} remove - Failed"
done
exit 0
