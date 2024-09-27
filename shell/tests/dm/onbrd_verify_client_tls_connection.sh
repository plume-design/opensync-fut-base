#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
onbrd/onbrd_verify_client_tls_connection.sh [-h]
Description:
    - Validate CM connecting to specific Cloud TLS version
Arguments:
    -h  show this help message
    \$1 (certs_dir) : Path to device certificates : (string)(optional) : (default:/var/certs)
Script usage example:
    ./onbrd/onbrd_verify_client_tls_connection.sh
    ./onbrd/onbrd_verify_client_tls_connection.sh /var/certs
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

cert_dir=${1:-"/var/certs"}

log_title "onbrd/onbrd_verify_client_tls_connection.sh: ONBRD test - Verify client TLS connection"


log "onbrd/onbrd_verify_client_tls_connection.sh: Checking if the 'ca_cert' field in the SSL OVSDB table is populated"
wait_for_function_response "notempty" "get_ovsdb_entry_value SSL ca_cert" &&
    log "onbrd/onbrd_verify_client_tls_connection.sh: The 'ca_cert' field in the SSL OVSDB table is populated - Success" ||
    raise "The 'ca_cert' field in the SSL OVSDB table is not populated. Terminating test" -l "onbrd/onbrd_verify_client_tls_connection.sh" -tc

# Retrieve the CA certificate file from the SSL OVSDB table
ssl_ca_cert_org="$(get_ovsdb_entry_value SSL ca_cert)"

log "onbrd/onbrd_verify_client_tls_connection.sh: Checking if the 'ca_cert' file exists"
[ -e "$ssl_ca_cert_org" ] &&
    log "onbrd/onbrd_verify_client_tls_connection.sh: The $ssl_ca_cert_org CA certificate file exists - Success" ||
    raise "The $ssl_ca_cert_org CA certificate file does not exist. Terminating test" -l "onbrd/onbrd_verify_client_tls_connection.sh" -tc

log "onbrd/onbrd_verify_client_tls_connection.sh: Saving state of AWLAN_Node, SSL ovsdb tables for a later revert"
an_redirector_addr_org="$(get_ovsdb_entry_value AWLAN_Node redirector_addr)"
log -deb "onbrd/onbrd_verify_client_tls_connection.sh: Backup values"
log -deb "   SSL        :: ca_cert          := ${ssl_ca_cert_org}"
log -deb "   AWLAN_Node :: redirector_addr  := ${an_redirector_addr_org}"
log -deb "Device certificate dir = ${cert_dir}"

log "onbrd/onbrd_verify_client_tls_connection.sh: Making a copy of the current ca.pem for a later revert"
[ -e "${cert_dir}/original_ca.pem" ] || cat "${ssl_ca_cert_org}" > "${cert_dir}/original_ca.pem"

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables SSL Manager AWLAN_Node
    fut_info_dump_line
    [ -n "${ssl_ca_cert_org}" ] && update_ovsdb_entry SSL -u ca_cert "${ssl_ca_cert_org}" || true
    [ -n "${an_redirector_addr_org}" ] && update_ovsdb_entry AWLAN_Node -u redirector_addr "${an_redirector_addr_org}" || true
    cat ${cert_dir}/original_ca.pem > ${ssl_ca_cert_org} && rm ${cert_dir}/original_ca.pem
    exit $fut_ec
' EXIT INT TERM

connect_to_fut_cloud -cd "${cert_dir}" &&
    log "onbrd/onbrd_verify_client_tls_connection.sh: Device connected to FUT cloud. Start test case execution - Success" ||
    raise "Failed to connect device to FUT cloud. Terminate test" -l "onbrd/onbrd_verify_client_tls_connection.sh" -tc

# Check if connection is maintained for 60s
log "onbrd/onbrd_verify_client_tls_connection.sh: Checking if connection is maintained and stable"
for interval in $(seq 1 3); do
    log "onbrd/onbrd_verify_client_tls_connection.sh: Sleeping for 20 seconds"
    sleep 20
    log "onbrd/onbrd_verify_client_tls_connection.sh: Check connection status in Manager table is ACTIVE, check num: $interval"
    ${OVSH} s Manager status -r | grep "ACTIVE" &&
        log "onbrd/onbrd_verify_client_tls_connection.sh: wait_cloud_state - Connection state is ACTIVE, check num: $interval - Success" ||
        raise "wait_cloud_state - Connection state is NOT ACTIVE, check num: $interval, connection should be maintained" -l "onbrd/onbrd_verify_client_tls_connection.sh" -tc
done

pass
