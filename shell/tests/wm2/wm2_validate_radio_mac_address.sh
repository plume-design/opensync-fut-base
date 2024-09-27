#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"

usage()
{
cat << usage_string
wm2/wm2_validate_radio_mac_address.sh [-h] arguments
Description:
    - Script validates radio mac address in OVSDB with mac address from OS - LEVEL2
Arguments:
    -h  show this help message
    \$1  (if_name)        : interface name to validate address           : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_validate_radio_mac_address.sh <IF_NAME>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "wm2/wm2_validate_radio_mac_address.sh" -arg
if_name=${1}

log_title "wm2/wm2_validate_radio_mac_address.sh: WM2 test - Verifying OVSDB hwaddr with ${if_name} MAC from OS"

# Step 1 get MAC from OS
mac_address_os=$(get_mac_from_os "${if_name}")
log -deb "wm2/wm2_validate_radio_mac_address.sh - OS MAC address: '$mac_address_os'"

# Validate MAC format
validate_mac "$mac_address_os" &&
    log -deb "wm2/wm2_validate_radio_mac_address.sh - OS MAC address: '$mac_address_os' is validated - Success" ||
    raise "OS MAC address is not valid: '$mac_address_os'" -l "wm2/wm2_validate_radio_mac_address.sh" -fc

# Step 2 compare MAC from os and MAC from OVSDB
mac_address_ovsdb=$(${OVSH} s Wifi_Radio_State -w if_name=="$if_name" mac -r)
log -deb "wm2/wm2_validate_radio_mac_address.sh - OVSDB MAC address: '$mac_address_ovsdb'"

if [ "$mac_address_ovsdb" == "$mac_address_os" ]; then
    log -deb "wm2/wm2_validate_radio_mac_address.sh - MAC address: '$mac_address' at OS match MAC address: '$mac_address_ovsdb' from OVSDB - Success"
else
    raise "MAC address: '$mac_address' from OS does not match MAC address: '$mac_address_ovsdb' from OVSDB" -l "wm2/wm2_validate_radio_mac_address.sh" -tc
fi

pass
