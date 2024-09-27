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
tools/device/flush_iptables_chain.sh [-h] arguments
Description:
    - Flushes the desired chain(s) in iptables. Multiple chains can be specified.
Arguments:
    -h  show this help message
    - \$@ (chain) : Name of chain that will be flushed : (string)(required)
Script usage example:
    ./tools/device/flush_iptables_chain.sh MINIUPNPD
usage_string
}

log_title "tools/device/flush_iptables_chain.sh: flush_iptables_chain - Flushing the specified chain(s) from iptables rules"

for chain in "$@"
do
    iptables -F "$chain" &&
        log -deb "tools/device/flush_iptables_chain.sh: Flushed the $chain chain - Success" ||
        raise "flush_iptables_chain - Failed to flush the $chain chain" -l "tools/device/flush_iptables_chain.sh" -tc
done


exit 0
