#!/bin/bash

current_dir=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
export FUT_TOPDIR="$(realpath "$current_dir"/../../..)"

# FUT environment loading
# Script echoes single line so we are redirecting source output to /dev/null
source "${FUT_TOPDIR}/shell/config/default_shell.sh" &> /dev/null
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" &> /dev/null

usage()
{
cat << usage_string
tools/server/get_common_name_from_certificate.sh [-h]
Description:
    This script echoes the common name in the client certificate.
Options:
    -h  show this help message
Arguments:
    client_cert=$1  -- client certificate used to extract common name - (string)(required)
Script usage example:
    ./tools/server/get_common_name_from_certificate.sh "client.pem"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/server/get_common_name_from_certificate.sh" -arg

client_cert=${1}
cert_file="${FUT_TOPDIR}/${client_cert}"

comm_name=$(openssl x509 -in $cert_file -noout -subject | sed 's/.*CN = //;s/,.*//' | tr '[:lower:]' '[:upper:]')
[ -z ${comm_name} ] && raise "Could not parse CN from certificate ${cert_file}" -l "tools/server/get_common_name_from_certificate.sh" -fc
echo -n "${comm_name}"
