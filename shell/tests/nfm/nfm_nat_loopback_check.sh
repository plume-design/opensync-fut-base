#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"

usage()
{
cat << usage_string
nfm/nfm_nat_loopback_check.sh [-h] arguments
Description:
    - This script will enable NAT loopback functionality by configuring template rules in the Netfilter table.
Arguments:
    -h : show this help message
    - \$1 (gw_lan_ip)    : GW LAN IP address                : (string)(required)
    - \$2 (server_ip)    : IP of the local server device    : (string)(required)
    - \$3 (port)         : Port number                      : (int)(required)

Script usage example:
    ./nfm/nfm_nat_loopback_check.sh 192.168.4.10 192.168.40.14 55687
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/client/run_upnp_client.sh" -arg
gw_lan_ip=${1}
server_ip=${2}
port=${3}

log_title "nfm/nfm_nat_loopback_check.sh: Configure Netfilter entries for NAT loopback"

insert_ovsdb_entry Netfilter \
    -i chain "NFM_PREROUTING" \
    -i enable true \
    -i name "pf.prerouting" \
    -i priority 0 \
    -i protocol "ipv4" \
    -i rule "-p tcp --dport $port --to-destination $server_ip:$port" \
    -i status "enabled" \
    -i table "nat" \
    -i target "DNAT" ||
        raise "Could not insert entry to Netfilter table" -l "nfm/nfm_nat_loopback_check" -fc

insert_ovsdb_entry Netfilter \
    -i chain "NFM_POSTROUTING" \
    -i enable true \
    -i name "pf.postrouting" \
    -i priority 0 \
    -i protocol "ipv4" \
    -i rule "-p tcp -d $server_ip --dport $port --to-source $gw_lan_ip" \
    -i status "enabled" \
    -i table "nat" \
    -i target "SNAT" ||
        raise "Could not insert entry to Netfilter table" -l "nfm/nfm_nat_loopback_check" -fc
