#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

def_n_ping=2
def_ip="1.1.1.1"
usage()
{
cat << usage_string
tools/device/check_wan_connectivity.sh [-h] arguments
Description:
    - Script checks device L3 upstream connectivity with ping tool
Dependency:
    - "ping" tool with "-c" option to specify number of packets sent
Arguments:
    -h                        : Show this help message
    - \$1 (n_ping)            : How many packets are sent                    : (int)(optional)(default=${def_n_ping})
    - \$2 (internet_check_ip) : IP address to validate internet connectivity : (string)(optional)(default=${def_ip})
Script usage example:
    ./tools/device/check_wan_connectivity.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    if [ $fut_ec -ne 0 ]; then
        print_tables WAN_Config Wifi_Route_Config Wifi_Route_State
    fi
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

n_ping=${1:-$def_n_ping}
internet_check_ip=${2:-$def_ip}

wait_for_function_response 0  "ping -c${n_ping} ${internet_check_ip}" &&
    log "tools/device/check_wan_connectivity.sh: Can ping internet" ||
    raise "Can not ping internet" -l "tools/device/check_wan_connectivity.sh" -tc
