#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../../..)"
export FUT_TOPDIR=${fut_topdir}
source "${fut_topdir}/shell/lib/unit_lib.sh"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
address_dns_man.sh [-h] ip_address type
Options:
    -h  show this help message
Arguments:
    ip_address=$1 -- IP address to perform action on - (string)(required)
    type=$2 -- type of action to perform: block/unblock - (string)(required)
Usage:
    ./shell/tools/server/cm/address_dns_man.sh "192.168.200.11" "block"
    ./shell/tools/server/cm/address_dns_man.sh "192.168.200.10" "unblock"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "address_dns_man.sh" -arg
ip_address=${1}
type=${2}

log "address_dns_man.sh: Manipulate DNS traffic: ${type} ${ip_address}"
address_dns_manipulation "$ip_address" "$type"
