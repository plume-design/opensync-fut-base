#!/bin/bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
get_common_name_from_certificate.sh [-h]
Description:
    This script echoes the common name in the client certificate.
Options:
    -h  show this help message
Arguments:
    client_cert=$1  -- client certificate used to extract common name - (string)(required)
Script usage example:
    ./shell/tools/server/get_common_name_from_certificate.sh "client.pem"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "get_common_name_from_certificate.sh" -arg

client_cert=${1}
cert_file="${fut_topdir}/${client_cert}"

chmod 644 ${cert_file}
comm_name=$(openssl x509 -in $cert_file -noout -subject | sed 's/.*CN = //;s/,.*//' | tr '[a-z]' '[A-Z]')
[ -z ${comm_name} ] && raise "Could not parse CN from certificate ${cert_file}" -l "get_common_name_from_certificate.sh" -fc
echo -n "${comm_name}"
