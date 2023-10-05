#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

usage()
{
cat << usage_string
tools/device/clear_port_forward_in_iptables.sh [-h] arguments
Description:
    - Flushes the MINIUPnPD chain in the iptables
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/clear_port_forward_in_iptables.sh
usage_string
}

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/device/clear_port_forward_in_iptables.sh" -arg

log_title "tools/device/clear_port_forward_in_iptables.sh: clear_port_forward_in_iptables - Flushing the MINIUPnPD chain from iptable rules"
iptables -F MINIUPNPD &&
    log -deb "tools/device/clear_port_forward_in_iptables.sh: clear_port_forward_in_iptables - Success" ||
    raise "FAIL: clear_port_forward_in_iptables - Failed to flush the MINIUPNPD table" -l "tools/device/clear_port_forward_in_iptables.sh" -tc

exit 0
