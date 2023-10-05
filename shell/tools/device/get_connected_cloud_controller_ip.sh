#!/bin/sh

# FUT environment loading
# Script echoes single line so we are redirecting source output to /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source /tmp/fut-base/shell/config/default_shell.sh &> /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" &> /dev/null
[ -n "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -n "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

usage()
{
cat << usage_string
tools/device/get_connected_cloud_controller_ip.sh [-h] arguments
Description:
    - This script echoes the cloud controller ip which DUT is connected to. The IP is fetched
        from 'target' field of Manager table.
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/get_connected_cloud_controller_ip.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires no input argument(s)" -l "tools/device/get_connected_cloud_controller_ip.sh" -arg

get_target_str="get_ovsdb_entry_value Manager target -r"
wait_for_function_output "notempty" "${get_target_str}" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    resolved_target_addr=$($get_target_str) || raise "FAIL: ${get_target_str}"  -l "tools/device/get_connected_cloud_controller_ip.sh" -f
else
    raise "FAIL: Failed to get 'target' from Manager table" -l "tools/device/get_connected_cloud_controller_ip.sh" -s
fi

connected_cloud_ip=$(echo ${resolved_target_addr}| egrep -o '([0-9]{1,3}\.){3}[0-9]{1,3}')
echo -n "${connected_cloud_ip}"
