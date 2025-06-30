#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../../..)"
export FUT_TOPDIR=${fut_topdir}
source "${fut_topdir}/shell/lib/unit_lib.sh"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
manipulate_cloud_ip_addresses.sh [-h] ip_address type
Options:
    -h  show this help message
Arguments:
    hostname=$1         --   hostname of the redirector                 -   (string)(required)
    controller_ip=$2    --   IP address of the cloud controller         -   (string)(required)
    type=$3             --   type of action to perform: block/unblock   -   (string)(required)
Usage:
    ./shell/tools/server/cm/manipulate_cloud_ip_addresses.sh "www.redirector.com" "12.34.45.56" "block"
    ./shell/tools/server/cm/manipulate_cloud_ip_addresses.sh "www.redirector.com" "12.34.45.56" "unblock"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "manipulate_cloud_ip_addresses.sh" -arg

hostname=${1}
controller_ip=${2}
type=${3}

log "manipulate_cloud_ip_addresses.sh: Manipulate/${type} the cloud controller and redirector IPs"

ip_list=$(getent ahosts $hostname | grep -w "STREAM" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}')
for ip in $ip_list
do
    manipulate_cloud_controller_traffic $ip $type &&
        log "cm/manipulate_cloud_ip_addresses.sh: IP address '$ip' ${type}-ed - Success" ||
        raise "failed to $type IP $ip" -l "cm/manipulate_cloud_ip_addresses.sh" -tc
done

manipulate_cloud_controller_traffic $controller_ip $type &&
    log "cm/manipulate_cloud_ip_addresses.sh: IP address '$controller_ip' ${type}-ed - Success" ||
    raise "failed to $type IP $controller_ip" -l "cm/manipulate_cloud_ip_addresses.sh" -tc
