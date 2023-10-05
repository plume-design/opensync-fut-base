#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "$fut_topdir/lib/rpi_lib.sh"

usage()
{
cat << usage_string
tools/server/cm/address_dns_man.sh [-h] ip_address type
Options:
    -h  show this help message
Arguments:
    ip_address=$1 -- IP address to perform action on - (string)(required)
    type=$2 -- type of action to perform: block/unblock - (string)(required)
Usage:
   tools/server/cm/address_dns_man.sh "192.168.200.11" "block"
   tools/server/cm/address_dns_man.sh "192.168.200.10" "unblock"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/server/cm/address_dns_man.sh" -arg
ip_address=${1}
type=${2}

log "tools/server/cm/address_dns_man.sh: Manipulate DNS traffic: ${type} ${ip_address}"
address_dns_manipulation "$ip_address" "$type"
