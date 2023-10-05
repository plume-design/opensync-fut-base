#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "$fut_topdir/lib/rpi_lib.sh"

usage()
{
cat << usage_string
tools/server/um/create_md5_file.sh [-h] arguments
Description:
    - Creates MD5 file of FW image
Arguments:
    -h  show this help message
    \$1 (um_fw_path) : path to clean FW which to create corrupted copy : (string)(required)
Script usage example:
    ./tools/server/um/create_md5_file.sh /tmp/clean_device_fw.img
Result:
    - Creates MD5 file for FW image (example clean_device_fw.img.md5)
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/server/um/create_md5_file.sh" -arg
um_fw_path=$1

log "tools/server/um/create_md5_file.sh - Creating md5 sum file of file $um_fw_path"
create_md5_file "$um_fw_path" &&
    log -deb "tools/server/um/create_md5_file.sh - md5 sum file created - Success" ||
    raise "FAIL: Could not create md5 sum file" -l "tools/server/um/create_md5_file.sh" -ds
