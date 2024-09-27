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
tools/server/cm/manipulate_cloud_ip_addresses.sh [-h] ip_address type
Options:
    -h  show this help message
Arguments:
    hostname=$1         --   hostname of the redirector                 -   (string)(required)
    controller_ip=$2    --   IP address of the cloud controller         -   (string)(required)
    type=$3             --   type of action to perform: block/unblock   -   (string)(required)
Usage:
   tools/server/cm/manipulate_cloud_ip_addresses.sh "www.redirector.com" "12.34.45.56" "block"
   tools/server/cm/manipulate_cloud_ip_addresses.sh "www.redirector.com" "12.34.45.56" "unblock"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/server/cm/manipulate_cloud_ip_addresses.sh" -arg

hostname=${1}
controller_ip=${2}
type=${3}

log "tools/server/cm/manipulate_cloud_ip_addresses.sh: Manipulate/${type} the cloud controller and redirector IPs"

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
