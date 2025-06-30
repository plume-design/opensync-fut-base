#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat <<usage_string
tools/device/validate_port_forward_entry_in_iptables.sh [-h] arguments
Description:
    - Script checks port forwarding rule in the iptable on DUT.
Arguments:
    -h  show this help message
    - \$1 (client_ip_addr)      : IP address to validate entry in the iptable   : (string)(required)
    - \$2 (port_num)            : Port number to validate entry in the iptable  : (interger)(required)

Script usage example:
    ./tools/device/validate_port_forward_entry_in_iptables.sh 10.10.10.20 5201
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    iptables -t nat -vnL
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument" -arg
client_ip_addr=$1
port_num=$2

log_title "tools/device/validate_port_forward_entry_in_iptables.sh: Verify port forwarding in the iptable rules"

wait_for_function_response 0 "iptables -t nat -vnL | grep -E \"tcp dpt:${port_num}.*to:${client_ip_addr}:${port_num}\"" &&
    log -deb "tools/device/validate_port_forward_entry_in_iptables.sh: Port number ${port_num} is successfully forwarded - Success" ||
    raise "Port number ${port_num} failed to forward!" -l "tools/device/validate_port_forward_entry_in_iptables.sh" -tc
