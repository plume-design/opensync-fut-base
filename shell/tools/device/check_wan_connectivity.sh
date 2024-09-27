#!/bin/sh

# FUT environment loading
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

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

wait_for_function_response 0  "ping -c${n_ping} ${internet_check_ip}"
if [ $? -eq 0 ]; then
    log "tools/device/check_wan_connectivity.sh: Can ping internet"
    exit 0
else
    log -err "tools/device/check_wan_connectivity.sh: Can not ping internet"
    exit 1
fi
