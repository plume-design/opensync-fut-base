#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="vpnm/vpnm_setup.sh"
usage()
{
cat << usage_string
vpnm/vpnm_ipsec_vpn_healthcheck.sh [-h] arguments
Description:
    - The goal of this testcase is to verify if VPN healthcheck is functional.

Arguments:
    -h : show this help message

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./vpnm/vpnm_ipsec_vpn_healthcheck.sh
Script usage example:
    ./vpnm/vpnm_ipsec_vpn_healthcheck.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "vpnm/vpnm_ipsec_vpn_healthcheck.sh" -arg

trap '
fut_info_dump_line
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

check_ovsdb_table_exist VPN_Tunnel &&
    log "vpnm/vpnm_ipsec_vpn_healthcheck.sh: VPN_Tunnel table exists in ovsdb - Success" ||
    raise "FAIL: VPN_Tunnel table does not exist in ovsdb" -l "vpnm/vpnm_ipsec_vpn_healthcheck.sh" -s

empty_ovsdb_table VPN_Tunnel
empty_ovsdb_table IPSec_Config
empty_ovsdb_table IPSec_State
empty_ovsdb_table Tunnel_Interface

log "vpnm/vpnm_ipsec_vpn_healthcheck.sh: Inserting a VPN_Tunnel row with dummy healthcheck config"
insert_ovsdb_entry VPN_Tunnel \
    -i name "verify-healthcheck" \
    -i enable true \
    -i healthcheck_enable true \
    -i healthcheck_ip 8.8.8.8 \
    -i healthcheck_interval 5 \
    -i healthcheck_timeout 30 &&
        log "vpnm/vpnm_ipsec_vpn_healthcheck.sh: insert_ovsdb_entry - VPN_Tunnel - Success" ||
        raise "FAIL: insert_ovsdb_entry - VPN_Tunnel" -l "vpnm/vpnm_ipsec_vpn_healthcheck.sh" -oe

log "vpnm/vpnm_ipsec_vpn_healthcheck.sh: Checking if VPN Healthcheck up and running"

wait_ovsdb_entry VPN_Tunnel \
    -w name "verify-healthcheck" \
    -is healthcheck_status "ok" &&
        log "vpnm/vpnm_ipsec_vpn_healthcheck.sh: VPN Healthcheck running - Success" ||
        raise "FAIL: VPN Healthcheck NOT initiated" -l "vpnm/vpnm_ipsec_vpn_healthcheck.sh" -oe

pass
