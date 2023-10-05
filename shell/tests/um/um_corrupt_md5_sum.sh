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
create_corrupt_md5_file_path="tools/server/um/create_corrupt_md5_file.sh"
um_image_name_default="um_corrupt_md5_sum_fw"
usage()
{
cat << usage_string
um/um_corrupt_md5_sum.sh [-h] arguments
Description:
    - Script validates AWLAN_Node 'upgrade_status' field proper code change if corrupt md5 sum is downloaded, fails otherwise
Arguments:
    -h  show this help message
    \$1 (fw_path) : download path of UM - used to clear the folder on UM setup  : (string)(required)
    \$2 (fw_url)  : used as firmware_url in AWLAN_Node table                    : (string)(required)
Testcase procedure:
    - On RPI SERVER: Prepare clean FW (.img) in ${um_resource_path}
                     Duplicate image with different name (example. ${um_image_name_default}_tmp.img) (cp <CLEAN-IMG> <NEW-IMG>)
                     Create corrupted MD5 sum of duplicated FW image (example. ${um_image_name_default}.img.md5) (see ${create_corrupt_md5_file_path} -h)
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./um/um_corrupt_md5_sum.sh <FW-PATH> <FW-URL>
Script usage example:
    ./um/um_corrupt_md5_sum.sh /tmp/pfirmware http://fut.opensync.io:8000/fut-base/resource/um/${um_image_name_default}.img
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "um/um_corrupt_md5_sum.sh" -arg
fw_path=$1
fw_url=$2

trap '
    fut_info_dump_line
    print_tables AWLAN_Node
    reset_um_triggers $fw_path || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "um/um_corrupt_md5_sum.sh: UM test - Corrupt MD5 Sum"

log "um/um_corrupt_md5_sum.sh: Setting firmware_url to $fw_url"
update_ovsdb_entry AWLAN_Node -u firmware_url "$fw_url" &&
    log "um/um_corrupt_md5_sum.sh: update_ovsdb_entry - AWLAN_Node::firmware_url set to $fw_url - Success" ||
    raise "FAIL: update_ovsdb_entry - Failed to set firmware_url to $fw_url in AWLAN_Node" -l "um/um_corrupt_md5_sum.sh" -oe

fw_start_code=$(get_um_code "UPG_STS_FW_DL_START")
log "um/um_corrupt_md5_sum.sh: Waiting for FW download to start"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$fw_start_code" &&
    log "um/um_corrupt_md5_sum.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $fw_start_code - Success" ||
    raise "FAIL: wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $fw_start_code" -l "um/um_corrupt_md5_sum.sh" -tc

fw_err_code=$(get_um_code "UPG_ERR_MD5_FAIL")
log "um/um_corrupt_md5_sum.sh: Waiting for AWLAN_Node::upgrade_status to become UPG_ERR_MD5_FAIL ($fw_err_code)"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$fw_err_code" &&
    log "um/um_corrupt_md5_sum.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $fw_err_code - Success" ||
    raise "FAIL: wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $fw_err_code" -l "um/um_corrupt_md5_sum.sh" -tc

pass
