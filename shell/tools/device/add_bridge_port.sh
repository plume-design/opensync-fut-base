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
tools/device/add_bridge_port.sh [-h] arguments
Description:
    - Add bridge port through ovs-vsctl
Arguments:
    -h  show this help message
    - \$1 (bridge) : Bridge interface name      : (string)(required)
    - \$2 (port)   : Bridge port interface name : (string)(required)
Script usage example:
    ./tools/device/add_bridge_port.sh br-home home-ap-l50
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
bridge=${1}
port_if=${2}

add_bridge_port "${bridge}" "${port_if}" &&
    log -deb "tools/device/add_bridge_port.sh: Interface ${port_if} successfully added to bridge ${bridge}" ||
    raise "Failed to add interface ${port_if} to bridge ${bridge}" -l "tools/device/add_bridge_port.sh" -ds

exit 0
