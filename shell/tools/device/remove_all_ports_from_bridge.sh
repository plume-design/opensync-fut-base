#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tools/device/remove_all_ports_from_bridge.sh [-h] arguments
Description:
    - Remove all ports from bridge on device
Arguments:
    -h  show this help message
    - \$1 (bridge) : Bridge name : (string)(required)
Script usage example:
    ./tools/device/remove_all_ports_from_bridge.sh br-home
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
bridge=${1}

remove_all_ports_from_bridge "${bridge}" &&
    log -deb "tools/device/remove_all_ports_from_bridge.sh: All ports successfully removed from bridge ${bridge}" ||
    raise "Failed to remove all ports from bridge ${bridge}" -l "tools/device/remove_all_ports_from_bridge.sh" -ds

exit 0
