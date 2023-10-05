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
othr/othr_verify_eth_wan_iface_wifi_master_state.sh [-h] arguments
Description:
    - Verify Wifi_Master_State table exists and has if_name field populated.
Arguments:
    -h  show this help message
    \$1 (eth_wan_if_name)     : Ethernet WAN interface to be checked : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./othr/othr_verify_eth_wan_iface_wifi_master_state.sh <ETH_WAN_IF_NAME>
Script usage example:
    ./othr/othr_verify_eth_wan_iface_wifi_master_state.sh eth0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Master_State
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "othr/othr_verify_eth_wan_iface_wifi_master_state.sh" -arg
eth_wan_if_name=${1}

log_title "othr/othr_verify_eth_wan_iface_wifi_master_state.sh: ONBRD test - Verify Wifi_Master_State table exists and has eth wan interface '$eth_wan_if_name' populated"

${OVSH} s Wifi_Master_State
if [ $? -eq 0 ]; then
    log "othr/othr_verify_eth_wan_iface_wifi_master_state.sh: Wifi_Master_State table exists"
else
    raise "FAIL: Wifi_Master_State table does not exist" -l "othr/othr_verify_eth_wan_iface_wifi_master_state.sh" -tc
fi

check_ovsdb_entry Wifi_Master_State -w if_name $eth_wan_if_name
if [ $? -eq 0 ]; then
    log "othr/othr_verify_eth_wan_iface_wifi_master_state.sh: Wifi_Master_State populated with eth wan interface '$eth_wan_if_name' - Success"
else
    raise "FAIL: Wifi_Master_State not populated with eth wan interface '$eth_wan_if_name'" -l "othr/othr_verify_eth_wan_iface_wifi_master_state.sh" -tc
fi

pass
