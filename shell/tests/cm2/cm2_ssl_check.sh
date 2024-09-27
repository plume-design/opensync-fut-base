#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

cm_setup_file="cm2/cm2_setup.sh"
usage()
{
cat << usage_string
cm2/cm2_ssl_check.sh [-h]
Description:
    - Script checks for required SSL verification files used by CM contained in SSL table
      Test fails if any of the files is not present in given path or it is empty
Options:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${cm_setup_file} (see ${cm_setup_file} -h)
    - On DEVICE: Run: ./cm2/cm2_ssl_check.sh
Script usage example:
    ./cm2/cm2_ssl_check.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input arguments" -arg

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables SSL Manager Connection_Manager_Uplink
    ifconfig eth0
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "cm2/cm2_ssl_check.sh: CM2 test - SSL Check"

ca_cert_path=$(get_ovsdb_entry_value SSL ca_cert)
certificate_path=$(get_ovsdb_entry_value SSL certificate)
private_key_path=$(get_ovsdb_entry_value SSL private_key)

[ -e "$ca_cert_path" ] &&
    log "cm2/cm2_ssl_check.sh: ca_cert file is valid - $ca_cert_path - Success" ||
    raise "ca_cert file is missing - $ca_cert_path" -l "cm2/cm2_ssl_check.sh" -tc
[ -e "$certificate_path" ] &&
    log "cm2/cm2_ssl_check.sh: certificate file is valid - $certificate_path - Success" ||
    raise "certificate file is missing - $certificate_path" -l "cm2/cm2_ssl_check.sh" -tc
[ -e "$private_key_path" ] &&
    log "cm2/cm2_ssl_check.sh: private_key file is valid - $private_key_path - Success" ||
    raise "private_key file is missing - $private_key_path" -l "cm2/cm2_ssl_check.sh" -tc

[ -s "$ca_cert_path" ] &&
    log "cm2/cm2_ssl_check.sh: ca_cert file is not empty - $ca_cert_path - Success" ||
    raise "ca_cert file is empty - $ca_cert_path" -l "cm2/cm2_ssl_check.sh" -tc
[ -s "$certificate_path" ] &&
    log "cm2/cm2_ssl_check.sh: certificate file is not empty - $certificate_path - Success" ||
    raise "certificate file is empty - $certificate_path" -l "cm2/cm2_ssl_check.sh" -tc
[ -s "$private_key_path" ] &&
    log "cm2/cm2_ssl_check.sh: private_key file is not empty - $private_key_path - Success" ||
    raise "private_key file is empty - $private_key_path" -l "cm2/cm2_ssl_check.sh" -tc

pass
