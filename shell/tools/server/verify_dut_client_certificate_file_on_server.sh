#!/bin/bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
export FUT_TOPDIR=${fut_topdir}
source "${fut_topdir}/shell/lib/unit_lib.sh"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
verify_dut_client_certificate_file_on_server.sh [-h]
Description:
    Validate if the "client certificate" on DUT is signed by authentic CA and also validate
    other certificate parameters like Issuer, Common Name.
    The script is intended for execution on RPI server or local PC within the framework
    directory structure, not on DUT!
Options:
    -h  show this help message
Arguments:
    client_cert=$1  -- client certificate that needs to be validated against CA - (string)(required)
    ca_cert=$2      -- CA certificate file that is used to validate client certificate - (string)(required)
Script usage example:
    ./shell/tools/server/verify_dut_client_certificate_file_on_server.sh "client.pem" "ca.pem"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "verify_dut_client_certificate_file_on_server.sh" -arg

client_cert=${1}
ca_cert=${2}
plume_ca_file="ca_chain.pem"

plume_ca_dir="${fut_topdir}/shell/tools/server/files/"
plume_ca_path="${plume_ca_dir}/${plume_ca_file}"
cert_file="${fut_topdir}/${client_cert}"
ca_file="${fut_topdir}/${ca_cert}"

trap '
    fut_info_dump_line
    print_certificate_details $cert_file
    print_certificate_details $plume_ca_path
    print_certificate_details $ca_file
    fut_info_dump_line
' EXIT INT TERM

# TEST EXECUTION:
log "verify_dut_client_certificate_file_on_server.sh: Validating client certificate '$cert_file'..."

verify_client_certificate_file ${client_cert} ${ca_cert} ${plume_ca_file} &&
    log "verify_dut_client_certificate_file_on_server.sh: Validated client certificate - Success" ||
    raise "Client certificate verification failed" -l "verify_dut_client_certificate_file_on_server.sh" -tc

pass
