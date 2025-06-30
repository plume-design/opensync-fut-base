#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
{
cat << usage_string
create_corrupt_image_file.sh [-h] arguments
Description:
    - Creates corrupted FW image from clean image
Arguments:
    -h  show this help message
    \$1 (um_fw_path) : path to clean FW from which to create corrupted copy : (string)(required)
Script usage example:
    ./shell/tools/server/um/create_corrupt_image_file.sh /tmp/clean_device_fw.img
Result:
    - Creates corrupted FW image with 'corrupt_' prefix in name (example corrupt_clean_device_fw.img)
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "create_corrupt_image_file.sh" -arg
um_fw_path=$1

log "um_create_corrupt_image.sh - Creating $um_fw_path"
test -e "$um_fw_path" &&
    log -deb "um_create_corrupt_image.sh - ${um_fw_path} file exists - Success" ||
    raise "${um_fw_path} file does not exist" -l "um_create_corrupt_image.sh" -ds
um_create_corrupt_image "$um_fw_path" &&
    log -deb "um_create_corrupt_image.sh - Image corrupted - Success" ||
    raise "Could not corrupt image" -l "um_create_corrupt_image.sh" -ds
