#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
create_md5_file.sh [-h] arguments
Description:
    - Creates MD5 file of FW image
Arguments:
    -h  show this help message
    \$1 (um_fw_path) : path to FW image for which to create hash file : (string)(required)
Script usage example:
    ./shell/tools/server/um/create_md5_file.sh /tmp/clean_device_fw.img
Result:
    - Creates MD5 file for FW image (example clean_device_fw.img.md5)
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "create_md5_file.sh" -arg
um_fw_path=$1

log "create_md5_file.sh - Creating md5 sum file of file $um_fw_path"
test -e "$um_fw_path" &&
    log -deb "create_md5_file.sh - ${um_fw_path} file exists - Success" ||
    raise "${um_fw_path} file does not exist" -l "create_md5_file.sh" -ds
create_md5_file "$um_fw_path" &&
    log -deb "create_md5_file.sh - md5 sum file created - Success" ||
    raise "Could not create md5 sum file" -l "create_md5_file.sh" -ds
