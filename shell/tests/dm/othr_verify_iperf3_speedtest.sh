#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/othr_setup.sh"
usage()
{
cat << usage_string
othr/othr_verify_iperf3_speedtest.sh [-h] arguments
Description:
    - Script verifies iperf3 speedtest feature works on the DUT.
Arguments:
    -h  show this help message
    \$1 (server_ip_addr)     : IP address of the server                 : (string)(required)
    \$2 (traffic_type)       : Allowed values: forward, reverse, udp    : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./othr/othr_verify_iperf3_speedtest.sh <SERVER_IP_ADDRESS> <TRAFFIC_TYPE>
Script usage example:
    ./othr/othr_verify_iperf3_speedtest.sh 192.168.200.1 forward
    ./othr/othr_verify_iperf3_speedtest.sh 192.168.200.1 udp
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_verify_iperf3_speedtest.sh" -arg
server_ip_addr=${1}
traffic_type=${2}

log_title "othr/othr_verify_iperf3_speedtest.sh: OTHR test - Verify if iperf3 speedtest feature works on the DUT"

if [ ${traffic_type} == "forward" ]; then
    # Default traffic is TCP and uplink flow
    iperf3 -c ${server_ip_addr} -t 5 &&
        log "othr/othr_verify_iperf3_speedtest.sh: iperf3 client transferred uplink traffic to server - Success" ||
        raise "FAIL: iperf3 client failed to transfer traffic to server" -l "othr/othr_verify_iperf3_speedtest.sh" -tc
elif [ ${traffic_type} == "reverse" ]; then
    # Default traffic is TCP and -R option for downlink flow
    iperf3 -c ${server_ip_addr} -R -t 5 &&
        log "othr/othr_verify_iperf3_speedtest.sh: iperf3 client received the downlink traffic from the server - Success" ||
        raise "FAIL: iperf3 client failed to receive downlink traffic from the server" -l "othr/othr_verify_iperf3_speedtest.sh" -tc
elif [ ${traffic_type} == "udp" ]; then
    # Add option '-u' to iperf3 command for UDP traffic
    iperf3 -c ${server_ip_addr} -u -t 5 &&
        log "othr/othr_verify_iperf3_speedtest.sh: iperf3 client received the UDP traffic from the server - Success" ||
        raise "FAIL: iperf3 client failed to receive UDP traffic from the server" -l "othr/othr_verify_iperf3_speedtest.sh" -tc
else
    raise "FAIL: Invalid option supplied. Allowed options: 'forward', 'reverse', 'udp'" -l "othr/othr_verify_iperf3_speedtest.sh" -tc
fi

pass
