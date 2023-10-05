#!/bin/sh

# FUT environment loading
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source /tmp/fut-base/shell/config/default_shell.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -n "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}"
[ -n "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}"

usage()
{
cat << usage_string
tools/device/verify_dut_client_certificate_common_name.sh [-h] arguments
Description:
    Script validates the common name of the certificate against device
    parameters, like device model, device id or WAN eth interface MAC address.
Arguments:
    -h  show this help message
    - \$1 (cert_cn)           : Common Name of the certificate : (string)(required)
    - \$2 (interface)         : WAN interface name             : (string)(optional)
Script usage example:
    ./tools/device/verify_dut_client_certificate_common_name.sh PP203X eth0
    ./tools/device/verify_dut_client_certificate_common_name.sh 1A2B3C4D5E6F
usage_string
}
log "tools/device/verify_dut_client_certificate_common_name.sh - Verify common name of the certificate"

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -arg
cert_cn=${1}
interface=${2}

if [ -n ${interface} ]; then
    device_mac=$(get_radio_mac_from_system ${interface})
else
    device_mac=""
fi

device_model=$(get_ovsdb_entry_value AWLAN_Node model -r)
device_id=$(get_ovsdb_entry_value AWLAN_Node id -r)

common_name=$(echo "$cert_cn" | tr '[:lower:]' '[:upper:]')
model=$(echo "$device_model" | tr '[:lower:]' '[:upper:]')
id=$(echo "$device_id" | tr '[:lower:]' '[:upper:]')

check_certificate_cn $common_name $model $id $device_mac
[ $? -eq 0 ] &&
    log "tools/server/verify_dut_client_certificate_common_name.sh: Common Name: $cert_cn of certificate is valid" ||
    raise "tools/server/verify_dut_client_certificate_common_name.sh: Common Name: $cert_cn of certificate should match either of device model: $model, device id: $id or device mac: $device_mac" -l "tools/server/verify_dut_client_certificate_common_name.sh" -tc

pass
