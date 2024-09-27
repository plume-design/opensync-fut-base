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
usage()
{
cat << usage_string
um/um_download_image_while_downloading.sh [-h] arguments
Description:
    - Script verifies download of FW image if during the download process another
      download is triggered. Initial download should not be interrupted.

      Test requires some download rate limiter enabled so the image would not be downloaded
      in less than 10s. This enables the test to trigger an interruption during the download.

      Script populates AWLAN_Node table, upgrade_dl_timer and firmware_url fields and
      in effect triggers download.
      After update it checks if download is in progress by monitoring upgrade_status.
      If field contains code UPG_STS_FW_DL_START it is assumed download has started.

      Immediately after correct status code it starts another download by setting
      AWLAN_Node table again, but with different firmware_url (fw_url_2).

      Test assumes first download will not be interrupted.
      Script waits for upgrade_status field value to become UPG_STS_FW_DL_END.
      If so test passes.

Arguments:
    -h: show this help message
    \$1 (fw_path)     : download path for FW download at DUT - (string)(required)
    \$2 (fw_url)      : used as 1st firmware_url on RPI server in AWLAN_Node table - (string)(required)
    \$3 (fw_url_2)    : used as 2nd firmware_url on RPI server in AWLAN_Node table - (string)(required)
    \$4 (fw_dl_timer) : used as upgrade_dl_timer in AWLAN_Node table to initiate download procedure - (int)(required)

Testcase procedure:
    This script is executed on DUT.
    It is dependent on the following managers:
        - running UM manager
        - WAN connectivity to access FW image
    - On RPI SERVER: Prepare clean FW (.img) in ${um_resource_path}
                     Duplicate image with different name, use prefix in front of 1st name
                     Create md5 file for 2nd image
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./um/um_download_image_while_downloading.sh <FW-PATH> <FW-NAME-1> <FW-NAME-1> <fw_dl_timer>

Script usage example:
   um/um_download_image_while_downloading.sh "http://url_to_image image_name_1.img image_name_2.img 10"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=4
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "um/um_download_image_while_downloading.sh" -arg
fw_path=$1
fw_url=$2
fw_url_2=$3
fw_dl_timer=$4

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables AWLAN_Node
    reset_um_triggers $fw_path || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "um/um_download_image_while_downloading.sh: UM test - Download FW - upgrade_dl_timer - $fw_dl_timer seconds"

log "um/um_download_image_while_downloading.sh: Setting upgrade_dl_timer to $fw_dl_timer firmware_url to $fw_url"
update_ovsdb_entry AWLAN_Node \
    -u upgrade_dl_timer "$fw_dl_timer" \
    -u firmware_url "$fw_url" &&
        log "um/um_download_image_while_downloading.sh: update_ovsdb_entry - Success to update" ||
        raise "update_ovsdb_entry - Failed to update" -l "um/um_download_image_while_downloading.sh" -fc

start_time=$(date -D "%H:%M:%S"  +"%Y.%m.%d-%H:%M:%S")

log "um/um_download_image_while_downloading.sh: Waiting for FW download to start"
dl_start_code=$(get_um_code "UPG_STS_FW_DL_START")
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$dl_start_code" &&
    log "um/um_download_image_while_downloading.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $dl_start_code - Success" ||
    raise "wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $dl_start_code" -l "um/um_download_image_while_downloading.sh" -tc
log "um/um_download_image_while_downloading.sh: Download of 1st FW image started and in progress!"

# Download of first image started...
# ... now start with downloading new image (illegal or unexpected action).
log "um/um_download_image_while_downloading.sh: Starting another fw image download '$fw_url_2' while first one is still in progress"
update_ovsdb_entry AWLAN_Node \
    -u upgrade_dl_timer "$fw_dl_timer" \
    -u firmware_url "$fw_url_2" &&
        log "um/um_download_image_while_downloading.sh: update_ovsdb_entry - AWLAN_Node table updated - Success" ||
        raise "update_ovsdb_entry - AWLAN_Node table not updated" -l "um/um_download_image_while_downloading.sh" -fc

log "um/um_download_image_while_downloading.sh: Waiting for FW download to finish"
dl_end_code=$(get_um_code "UPG_STS_FW_DL_END")
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$dl_end_code" &&
    fw_download_result 0 "$start_time" ||
    fw_download_result 1 "$start_time"

pass
