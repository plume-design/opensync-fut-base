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
./tools/device/get_client_certificate.sh [-h] arguments
Description:
    - This script echoes either absolute path to client certificate file/CA file
      or just file names from the SSL table respectively.
Arguments:
    -h  show this help message
    \$1 (file_type) : 'cert_file' to get certificate file and 'ca_file' to get CA file: (string)(required)
    \$2 (query) : 'full_path' to echo full path to the files and 'file_name' to echo just filenames : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./tools/device/get_client_certificate.sh <FILE-TYPE> <QUERY-OPTION>
Script usage example:
    ./tools/device/get_client_certificate.sh "cert_file" "full_path"
    ./tools/device/get_client_certificate.sh "ca_file" "file_name"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/device/get_client_certificate.sh" -arg

file_type=${1}
query=${2}

if [ ${file_type} == "cert_file" ]; then
    file=$(get_ovsdb_entry_value SSL certificate -r)
elif [ ${file_type} == "ca_file" ]; then
    file=$(get_ovsdb_entry_value SSL ca_cert -r)
else
    raise "ARG1 - Wrong option provided" -l "tools/device/get_client_certificate.sh" -arg
fi

[ -e "$file" ] ||
    raise "'$file_type' is NOT present on DUT" -l "tools/device/get_client_certificate.sh" -tc

[ ${query} == "full_path" ] &&
    echo -n "${file}" && exit 0
[ ${query} == "file_name" ] &&
    echo -n "${file##*/}" && exit 0

raise "ARG2 - Wrong option provided" -l "tools/device/get_client_certificate.sh" -arg
