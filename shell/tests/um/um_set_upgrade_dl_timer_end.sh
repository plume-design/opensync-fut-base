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
um_image_name_default="um_set_upg_dl_timer_fw"
create_md5_file_path="tools/server/um/create_md5_file.sh"
usage()
{
cat << usage_string
um/um_set_upgrade_dl_timer_end.sh [-h] arguments
Description:
    Script validates UM upgrade_dl_timer is being respected while UM downloads the FW.
    Script fails if FW download is not finished within given time defined by upgrade_dl_timer in AWLAN_Node.
    Script passes if FW download is finished within given time defined by upgrade_dl_timer in AWLAN_Node.
    FW download is finished if upgrade_status in AWLAN_Node table reaches code value of UPG_STS_FW_DL_END.
Arguments:
    -h  show this help message
    \$1 (fw_path)      : download path of UM - used to clear the folder on UM setup  : (string)(required)
    \$2 (fw_url)       : used as firmware_url in AWLAN_Node table                    : (string)(required)
    \$3 (fw_dl_timer)  : used as upgrade_dl_timer in AWLAN_Node table                : (integer)(required)
Testcase procedure:
    - On RPI SERVER: Prepare clean FW (.img) in ${um_resource_path}
                     Duplicate image with different name (example. ${um_image_name_default}.img) (cp <CLEAN-IMG> <NEW-IMG>)
                     Create MD5 sum for image (example. ${um_image_name_default}.img.md5) (see ${create_md5_file_path} -h)
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./um/um_set_upgrade_dl_timer_end.sh <FW-PATH> <FW-URL> <UPGRADE_DL_TIMER>
Script usage example:
    ./um/um_set_upgrade_dl_timer_end.sh /tmp/pfirmware http://fut.opensync.io:8000/fut-base/resource/um/${um_image_name_default}.img 100
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "um/um_set_upgrade_dl_timer_end.sh" -arg
fw_path=$1
fw_url=$2
fw_dl_timer=$3

trap '
    fut_info_dump_line
    print_tables AWLAN_Node
    reset_um_triggers $fw_path || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "um/um_set_upgrade_dl_timer_end.sh: UM test - Download FW - upgrade_dl_timer - end"

log "um/um_set_upgrade_dl_timer_end.sh: Setting upgrade_dl_timer to $fw_dl_timer firmware_url to $fw_url"
update_ovsdb_entry AWLAN_Node \
    -u upgrade_dl_timer "$fw_dl_timer" \
    -u firmware_url "$fw_url" &&
        log "um/um_set_upgrade_dl_timer_end.sh: update_ovsdb_entry - AWLAN_Node updated - Success" ||
        raise "FAIL: update_ovsdb_entry - Failed to update AWLAN_Node" -l "um/um_set_upgrade_dl_timer_end.sh" -oe

start_time=$(date -D "%H:%M:%S"  +"%Y.%m.%d-%H:%M:%S")

fw_start_code=$(get_um_code "UPG_STS_FW_DL_START")
log "um/um_set_upgrade_dl_timer_end.sh: Waiting for FW download to start, AWLAN_Node::upgrade_status to become UPG_STS_FW_DL_START ('$dl_start_code')"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$fw_start_code" &&
    log "um/um_set_upgrade_dl_timer_end.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is $fw_start_code - Success" ||
    raise "FAIL: wait_ovsdb_entry - AWLAN_Node::upgrade_status is not $fw_start_code" -l "um/um_set_upgrade_dl_timer_end.sh" -tc

dl_end_code=$(get_um_code "UPG_STS_FW_DL_END")
log "um/um_set_upgrade_dl_timer_end.sh: Waiting for FW download to finish, AWLAN_Node::upgrade_status to become UPG_STS_FW_DL_END ('$dl_end_code')"
wait_ovsdb_entry AWLAN_Node -is upgrade_status "$dl_end_code"
if [ $? -eq 0 ]; then
{
    end_time=$(date -D "%H:%M:%S"  +"%Y.%m.%d-%H:%M:%S")
    t1=$(date -u -d "$start_time" +"%s")
    t2=$(date -u -d "$end_time" +"%s")
    download_time=$(( t2 - t1 ))
    log "um/um_set_upgrade_dl_timer_end.sh: wait_ovsdb_entry - AWLAN_Node::upgrade_status is '$dl_end_code', FW downloaded in $download_time secs - Success"
}
else
    raise "FAIL: wait_ovsdb_entry - Failed to set AWLAN_Node::upgrade_status to $dl_end_code, FW download not finished" -l "um/um_set_upgrade_dl_timer_end.sh" -tc
fi

pass
