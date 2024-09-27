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
tools/device/configure_dpi_tap_interface.sh [-h] arguments
Description:
    - Script configures tap interface required for DPI testcases
Arguments:
    -h  show this help message
    \$1 (lan_bridge_if)    : Interface name used for LAN bridge        : (string)(required)
Script usage example:
    ./tools/device/configure_dpi_tap_interface.sh br-wan
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
bridge=${1}
of_port=30001
tap_ifname=${bridge}.dpi

check_if_port_in_bridge "${bridge}" "${tap_ifname}"
if [ $? = 0 ]; then
    log -deb "tools/device/configure_dpi_tap_interface.sh: Port '${tap_ifname}' exists in bridge '${bridge}', removing..."
    remove_port_from_bridge "${bridge}" "${tap_ifname}" &&
        log -deb " tools/device/configure_dpi_tap_interface.sh: remove_port_from_bridge ${bridge} ${tap_ifname} - Success" ||
        raise "Could not remove port '${tap_ifname}' from bridge '${bridge}'" -l  "tools/device/configure_dpi_tap_interface.sh" -ds
fi

wait_for_function_response 0 "add_tap_interface ${bridge} ${tap_ifname} ${of_port}" &&
    log "tools/device/configure_dpi_tap_interface.sh: Add port '${tap_ifname}' to bridge ${bridge} - Success" ||
    raise "Could not add port '${tap_ifname}' to bridge ${bridge}" -l "tools/device/configure_dpi_tap_interface.sh:" -tc

wait_for_function_response 0 "ip link set ${tap_ifname} up" &&
    log "tools/device/configure_dpi_tap_interface.sh: Bring interface '${tap_ifname}' up - Success" ||
    raise "Could not bring interface '${tap_ifname}' up" -l "tools/device/configure_dpi_tap_interface.sh:" -tc

wait_for_function_response 0 "gen_no_flood_cmd ${bridge} ${tap_ifname}" &&
    log "tools/device/configure_dpi_tap_interface.sh: Set interface '${tap_ifname}' no-flood - Success" ||
    raise "Could not set interface '${tap_ifname}' no-flood" -l "tools/device/configure_dpi_tap_interface.sh:" -tc

exit 0
