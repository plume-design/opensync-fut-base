#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="um/um_setup.sh"
um_resource_path="resource/um/"
um_image_name_default="um_corrupt_fw"
usage()
{
cat << usage_string
um/um_corrupt_image.sh [-h] arguments
Description:
    - Script validates AWLAN_Node 'upgrade_status' field proper code change if corrupt image is downloaded, fails otherwise
Arguments:
    -h  show this help message
    \$1 (fw_path) : download path of UM - used to clear the folder on UM setup  : (string)(required)
    \$2 (fw_url)  : used as firmware_url in AWLAN_Node table                    : (string)(required)
Testcase procedure:
    - On RPI SERVER: Prepare clean FW (.img) in ${um_resource_path}
                     Duplicate image with different name (example. ${um_image_name_default}_tmp.img) (cp <CLEAN-IMG> <NEW-IMG>)
                     Create corrupted image of duplicated FW image (example. ${um_image_name_default}.img) (see shell/tools/server/um/create_md5_file.sh -h)
                     Create MD5 sum for corrupted image (example. ${um_image_name_default}.img.md5) (see tools/server/um/create_md5_file.sh -h)
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./um/um_corrupt_image.sh <FW-PATH> <FW-URL>
Script usage example:
    ./um/um_corrupt_image.sh /tmp/pfirmware http://fut.opensync.io:8000/fut-base/resource/um/${um_image_name_default}.img
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "um/um_corrupt_image.sh" -arg
fw_path=$1
fw_url=$2

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables AWLAN_Node
    reset_um_triggers $fw_path || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "um/um_corrupt_image.sh: UM test - Corrupt FW image"

log "um/um_corrupt_image.sh: Setting firmware_url to $fw_url"
update_ovsdb_entry AWLAN_Node -u firmware_url "$fw_url" &&
    log "um/um_corrupt_image.sh: update_ovsdb_entry - AWLAN_Node::firmware_url is $fw_url - Success" ||
    raise "update_ovsdb_entry - AWLAN_Node::firmware_url is not $fw_url" -l "um/um_corrupt_image.sh" -fc

fw_start_code=$(get_um_code "UPG_STS_FW_DL_START")
log "um/um_corrupt_image.sh: Waiting for FW download to start"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$fw_start_code" &&
    log "um/um_corrupt_image.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $fw_start_code - Success" ||
    raise "wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $fw_start_code" -l "um/um_corrupt_image.sh" -tc

fw_stop_code=$(get_um_code "UPG_STS_FW_DL_END")
log "um/um_corrupt_image.sh: Waiting for FW download to finish"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$fw_stop_code" &&
    log "um/um_corrupt_image.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $fw_stop_code - Success" ||
    raise "wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $fw_stop_code" -l "um/um_corrupt_image.sh" -tc

log "um/um_corrupt_image.sh: Setting AWLAN_Node upgrade_timer to 1 - Starting upgrade in 1 sec"
update_ovsdb_entry AWLAN_Node -u upgrade_timer 1 &&
    log "um/um_corrupt_image.sh: update_ovsdb_entry - AWLAN_Node::upgrade_timer is 1 - Success" ||
    raise "update_ovsdb_entry - AWLAN_Node::upgrade_timer is not 1" -l "um/um_corrupt_image.sh" -fc

fw_fail_code=$(get_um_code "UPG_ERR_FL_WRITE")
log "um/um_corrupt_image.sh: Waiting for AWLAN_Node::upgrade_status to become UPG_ERR_FL_WRITE ($fw_fail_code)"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$fw_fail_code" &&
    log "um/um_corrupt_image.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $fw_fail_code - Success" ||
    raise "wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $fw_fail_code" -l "um/um_corrupt_image.sh" -tc

pass
