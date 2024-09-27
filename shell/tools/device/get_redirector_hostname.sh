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
tools/device/get_redirector_hostname.sh [-h] arguments
Description:
    - This script echoes the hostname of the redirector. This is fetched
      from the 'redirector_addr' field of AWLAN_Node table.
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/get_redirector_hostname.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=0
[ $# -ne ${NARGS} ] && usage && raise "Requires no input argument(s)" -l "tools/device/get_redirector_hostname.sh" -arg

redirector_addr="get_ovsdb_entry_value AWLAN_Node redirector_addr -r"
wait_for_function_output "notempty" "${redirector_addr}" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    resolved_target_addr=$($redirector_addr) || raise "${redirector_addr}" -l "tools/device/get_redirector_hostname.sh" -fc
else
    raise "Failed to get 'redirector_addr' from AWLAN_Node table" -l "tools/device/get_redirector_hostname.sh" -s
fi

hostname=$(echo ${resolved_target_addr} | cut -d ":" -f2)
echo -n "${hostname}"
