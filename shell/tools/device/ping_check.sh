#!/bin/sh

# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh > /dev/null
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh > /dev/null
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh" > /dev/null

usage()
{
cat << usage_string
tools/device/ping_check.sh [-h]
Description:
    - Script pings the selected IP address and collects the statistics to the specified log file.
Arguments:
    -h  show this help message
    \$1 (ip_address)    : IP address to ping                  : (string)(required)
    \$2 (ping_log_file) : File containing the ping statistics : (string)(required)
Script usage example:
    ./tools/device/ping_check.sh 1.1.1.1 ping.log
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument" -l "tools/device/ping_check.sh" -arg

ip_address=${1}
ping_log_file=${2}

# Clear the log files contents
echo "" > "$ping_log_file"

for i in $(seq 1 300); do
    { date && ping -c 1 "$ip_address"; } >> "$ping_log_file"
    sleep 1
done
