#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="nm2/nm2_setup.sh"
usage()
{
cat << usage_string
nm2/nm2_ovsdb_ip_port_forward.sh [-h] arguments
Description:
    - Script checks if IP port forward rule is created on the system when configured either through IP_Port_Forward or
      Netfilter table. Script fails if IP port is not forwarded on the system
Arguments:
    -h  show this help message
    \$1 (src_ifname) : Source interface name              : (string)(required)
    \$2 (src_port)   : Sourcer port                       : (string)(required)
    \$3 (dst_ipaddr) : Destination IP address             : (string)(required)
    \$4 (dst_port)   : Destination port                   : (string)(required)
    \$5 (protocol)   : Protocol                           : (string)(required)
    \$6 (pf_table)   : OVSDB table used for iptables rule : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_ovsdb_ip_port_forward.sh <SRC-IFNAME> <SRC-PORT> <DST-IPADDR> <DST-PORT> <PROTOCOL> <PF_TABLE>
Script usage example:
    ./nm2/nm2_ovsdb_ip_port_forward.sh wifi0 8080 10.10.10.200 80 tcp Netfilter
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=6
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -arg
src_ifname=$1
src_port=$2
dst_ipaddr=$3
dst_port=$4
protocol=$5
pf_table=$6

trap '
    fut_info_dump_line
    print_tables IP_Port_Forward Netfilter
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_ovsdb_ip_port_forward.sh: NM2 test - Testing IP port forwarding"

log "nm2/nm2_ovsdb_ip_port_forward.sh: Set IP FORWARD in OVSDB"
set_ip_port_forwarding "$src_ifname" "$src_port" "$dst_ipaddr" "$dst_port" "$protocol" "$pf_table" &&
    log "nm2/nm2_ovsdb_ip_port_forward.sh: Set IP port forward for $src_ifname - Success" ||
    raise "FAIL: Failed to set IP port forward - $src_ifname" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -tc

log "nm2/nm2_ovsdb_ip_port_forward.sh: Check for IP FORWARD record in iptables - LEVEL2"
wait_for_function_response 0 "check_ip_port_forwarding $dst_ipaddr:$dst_port" &&
    log "nm2/nm2_ovsdb_ip_port_forward.sh: LEVEL2 - IP port forward record propagated to iptables" ||
    raise "FAIL: LEVEL2 - Failed to propagate record into iptables" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -tc

log "nm2/nm2_ovsdb_ip_port_forward.sh: Delete IP FORWARD from OVSDB"

if [ "$pf_table" = "Netfilter" ]; then
    ${OVSH} d "$pf_table" -w chain=="PF_PREROUTING" -w name=="pf.dnat_tcp_$src_ifname" &&
        log "nm2/nm2_ovsdb_ip_port_forward.sh: Deleted IP FORWARD for $src_ifname from Netfilter" ||
        raise "FAIL: Failed to delete IP FORWARD for $src_ifname from Netfilter" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -tc
    wait_ovsdb_entry_remove "$pf_table" -w chain "PF_PREROUTING" -w name "pf.dnat_tcp_$src_ifname" &&
        log "nm2/nm2_ovsdb_ip_port_forward.sh: Removed entry from Netfilter for $src_ifname - Success" ||
        raise "FAIL: Failed to remove entry from Netfilter for $src_ifname" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -tc
else
    ${OVSH} d "$pf_table" -w dst_ipaddr=="$dst_ipaddr" -w src_ifname=="$src_ifname" &&
        log "nm2/nm2_ovsdb_ip_port_forward.sh: Deleted IP FORWARD for $src_ifname from IP_Port_Forward" ||
        raise "FAIL: Failed to delete IP FORWARD for $src_ifname from IP_Port_Forward" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -tc
    wait_ovsdb_entry_remove "$pf_table" -w dst_ipaddr "$dst_ipaddr" -w src_ifname "$src_ifname" &&
        log "nm2/nm2_ovsdb_ip_port_forward.sh: Removed entry from IP_Port_Forward for $src_ifname - Success" ||
        raise "FAIL: Failed to remove entry from IP_Port_Forward for $src_ifname" -l "nm2/nm2_ovsdb_ip_port_forward.sh" -tc
fi

log "nm2/nm2_ovsdb_ip_port_forward.sh: Check is IP FORWARD record is deleted from iptables - LEVEL2"
wait_for_function_response 1 "check_ip_port_forwarding $dst_ipaddr:$dst_port" &&
    log "nm2/nm2_ovsdb_ip_port_forward.sh: LEVEL2 - IP FORWARD record deleted from iptables - Success" ||
    force_delete_ip_port_forward_raise "$src_ifname" "NM_PORT_FORWARD" "$dst_ipaddr:$dst_port"

pass
