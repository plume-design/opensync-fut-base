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
vpnm/vpnm_ipsec_tunnel_interface.sh [-h] arguments
Description:
    - Check if a virtual tunnel interface (VTI) can be successfully created by VPNM.
      This also checks the SDK integration / Linux kernel config enablement of VTI interfaces.
      VTI interfaces are well supported in the Linux kernel but embedded SDKs often do
      not enable them by default.
Arguments:
    -h : show this help message

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./vpnm/vpnm_ipsec_tunnel_interface.sh
Script usage example:
    ./vpnm/vpnm_ipsec_tunnel_interface.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "vpnm/vpnm_ipsec_tunnel_interface.sh" -arg

check_ovsdb_table_exist Tunnel_Interface &&
    log "vpnm/vpnm_ipsec_tunnel_interface.sh: Tunnel_Interface table exists in ovsdb - Success" ||
    raise "Tunnel_Interface table does not exist in ovsdb" -l "vpnm/vpnm_ipsec_tunnel_interface.sh" -s

empty_ovsdb_table VPN_Tunnel
empty_ovsdb_table IPSec_Config
empty_ovsdb_table IPSec_State
empty_ovsdb_table Tunnel_Interface

ip link del Tunnel0 2>/dev/null

log "vpnm/vpnm_ipsec_tunnel_interface.sh: Inserting a tunnel interface row"
insert_ovsdb_entry Tunnel_Interface \
    -i if_name Tunnel0 \
    -i if_type vti \
    -i enable true \
    -i local_endpoint_addr 192.168.200.10 \
    -i remote_endpoint_addr 8.8.8.8\
    -i key 10 &&
        log "vpnm/vpnm_ipsec_tunnel_interface.sh: insert_ovsdb_entry - Tunnel_Interface - Success" ||
        raise "insert_ovsdb_entry - Tunnel_Interface" -l "vpnm/vpnm_ipsec_tunnel_interface.sh" -fc

sleep 1

log "vpnm/vpnm_ipsec_tunnel_interface.sh: Checking if tunnel interface created"
ip link show Tunnel0 &&
    log "vpnm/vpnm_ipsec_tunnel_interface.sh: VTI tunnel interface created - Success" ||
    raise "VTI tunnel interface NOT created" -l "vpnm/vpnm_ipsec_tunnel_interface.sh" -fc

pass
