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
tools/device/remove_port_from_bridge.sh [-h] arguments
Description:
    - Remove port from bridge on device
Arguments:
    -h  show this help message
    - \$1 (bridge) : Bridge interface name      : (string)(required)
    - \$2 (port)   : Bridge port interface name : (string)(required)
Script usage example:
    ./tools/device/remove_port_from_bridge.sh br-home home-ap-l50
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
bridge=${1}
port_if=${2}

remove_port_from_bridge "${bridge}" "${port_if}" &&
    log -deb "tools/device/remove_port_from_bridge.sh: Interface ${port_if} successfully removed from bridge ${bridge}" ||
    raise "Failed to remove interface ${port_if} from bridge ${bridge}" -l "tools/device/remove_port_from_bridge.sh" -ds

exit 0
