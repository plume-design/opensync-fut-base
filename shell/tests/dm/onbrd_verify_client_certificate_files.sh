#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_client_certificate_files.sh [-h] arguments
Description:
    - Validate certificate files on devices
Arguments:
    -h  show this help message
    \$1 (cert_file) : Used to define specific cert file path from SSL table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_client_certificate_files.sh <CERT-FILE>
Script usage example:
    ./onbrd/onbrd_verify_client_certificate_files.sh ca_cert
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables SSL
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_client_certificate_files.sh" -arg
cert_file=$1
cert_file_path=$(get_ovsdb_entry_value SSL "$cert_file")

log_title "onbrd/onbrd_verify_client_certificate_files.sh: ONBRD test - Verify cert file '${cert_file}' is valid"

[ -e "$cert_file_path" ] &&
    log "onbrd/onbrd_verify_client_certificate_files.sh: file '$cert_file_path' exists - Success" ||
    raise "FAIL: file '$cert_file_path' is missing" -l "onbrd/onbrd_verify_client_certificate_files.sh" -tc

log "onbrd/onbrd_verify_client_certificate_files.sh: Verify file is not empty"
[ -s "$cert_file_path" ] &&
    log "onbrd/onbrd_verify_client_certificate_files.sh: file '$cert_file_path' is not empty - Success" ||
    raise "FAIL: file '$cert_file_path' is empty" -l "onbrd/onbrd_verify_client_certificate_files.sh" -tc

pass
