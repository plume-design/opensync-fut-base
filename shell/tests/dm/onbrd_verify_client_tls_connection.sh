#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
haproxy_cfg_path="tools/server/files/haproxy.cfg"
fut_cloud_start_path="tools/server/start_cloud_simulation.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_client_tls_connection.sh [-h]
Description:
    - Validate CM connecting to specific Cloud TLS version
Arguments:
    -h  show this help message
    \$1 (certs_dir) : Path to device certificates : (string)(optional) : (default:/var/certs)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
    - On RPI SERVER:
        - Edit ${haproxy_cfg_path} to change TLS version
            Look for:
              ssl-default-bind-options force-tlsv<TLS-VERSION> ssl-max-ver TLSv<TLS-VERSION> ssl-min-ver TLSv<TLS-VERSION>
              ssl-default-server-options force-tlsv<TLS-VERSION> ssl-max-ver TLSv<TLS-VERSION> ssl-min-ver TLSv<TLS-VERSION>
            Change <TLS-VERSION> to one of following: 1.0, 1.1. 1.2
        - Run ./${fut_cloud_start_path} -r
    - On DEVICE: Run: ./onbrd/onbrd_verify_client_tls_connection.sh
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

log "onbrd/onbrd_verify_client_tls_connection.sh: Setting CM log level to TRACE"
set_manager_log CM TRACE

log "onbrd/onbrd_verify_client_tls_connection.sh: Saving current state of AWLAN_Node/SSL ovsdb tables for a later revert"
# connect_to_fut_cloud() updates only SSL::ca_cert, save original for later use
ssl_ca_cert_org="$(get_ovsdb_entry_value SSL ca_cert)"
# connect_to_fut_cloud() updates AWLAN_Node::redirector_addr and Manager::inactivity_probe::min_backoff::max_backoff, save original for later use
an_redirector_addr_org="$(get_ovsdb_entry_value AWLAN_Node redirector_addr)"
m_inactivity_probe_org="$(get_ovsdb_entry_value Manager inactivity_probe)"
m_min_backoff_org="$(get_ovsdb_entry_value AWLAN_Node min_backoff)"
m_max_backoff_org="$(get_ovsdb_entry_value AWLAN_Node max_backoff)"
log -deb "onbrd/onbrd_verify_client_tls_connection.sh: Backup values"
log -deb "   SSL        :: ca_cert          := ${ssl_ca_cert_org}"
log -deb "   AWLAN_Node :: redirector_addr  := ${an_redirector_addr_org}"
log -deb "   Manager    :: inactivity_probe := ${m_inactivity_probe_org}"
log -deb "   AWLAN_Node :: min_backoff      := ${m_min_backoff_org}"
log -deb "   AWLAN_Node :: max_backoff      := ${m_max_backoff_org}"
log -deb "Device certificate dir = ${cert_dir}"

log "onbrd/onbrd_verify_client_tls_connection.sh: Making a copy of the current ca.pem for a later revert"
cat "${ssl_ca_cert_org}" > "${cert_dir}/original_ca.pem"

trap '
    fut_info_dump_line
    print_tables SSL Manager AWLAN_Node
    [ -n "${ssl_ca_cert_org}" ] && update_ovsdb_entry SSL -u ca_cert "${ssl_ca_cert_org}" || true
    [ -n "${an_redirector_addr_org}" ] && update_ovsdb_entry AWLAN_Node -u redirector_addr "${an_redirector_addr_org}" || true
    [ -n "${m_inactivity_probe_org}" ] && update_ovsdb_entry Manager -u inactivity_probe "${m_inactivity_probe_org}" || true
    [ -n "${m_min_backoff_org}" ] && update_ovsdb_entry AWLAN_Node -u min_backoff "${m_min_backoff_org}" || true
    [ -n "${m_max_backoff_org}" ] && update_ovsdb_entry AWLAN_Node -u max_backoff "${m_max_backoff_org}" || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

connect_to_fut_cloud -cd "${cert_dir}" &&
    log "onbrd/onbrd_verify_client_tls_connection.sh: Device connected to FUT cloud. Start test case execution - Success" ||
    raise "FAIL: Failed to connect device to FUT cloud. Terminate test" -l "onbrd/onbrd_verify_client_tls_connection.sh" -tc

# Check if connection is maintained for 60s
log "onbrd/onbrd_verify_client_tls_connection.sh: Checking if connection is maintained and stable"
for interval in $(seq 1 3); do
    log "onbrd/onbrd_verify_client_tls_connection.sh: Sleeping for 20 seconds"
    sleep 20
    log "onbrd/onbrd_verify_client_tls_connection.sh: Check connection status in Manager table is ACTIVE, check num: $interval"
    ${OVSH} s Manager status -r | grep "ACTIVE" &&
        log "onbrd/onbrd_verify_client_tls_connection.sh: wait_cloud_state - Connection state is ACTIVE, check num: $interval - Success" ||
        raise "FAIL: wait_cloud_state - Connection state is NOT ACTIVE, check num: $interval, connection should be maintained" -l "onbrd/onbrd_verify_client_tls_connection.sh" -tc
done

log "onbrd/onbrd_verify_client_tls_connection.sh: Reverting original ca.pem"
cat "${cert_dir}/original_ca.pem" > "${ssl_ca_cert_org}"

pass
