#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

dm_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_reboot_file_exists.sh [-h]
Description:
    - Script checks if reboot file holding the last reboot reason exist and is not empty.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${dm_setup_file} (see ${dm_setup_file} -h)
    - On DEVICE: Run: ./dm/dm_verify_reboot_file_exists.sh
Script usage example:
    ./dm/dm_verify_reboot_file_exists.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_OSP_REBOOT_PSTORE" "y" ||
    raise "CONFIG_OSP_REBOOT_PSTORE != y - Testcase not applicable REBOOT PERSISTENT STORAGE not supported" -l "dm/dm_verify_reboot_file_exists.sh" -s

reboot_file_path="/var/run/osp_reboot_reason"

log_title "dm/dm_verify_reboot_file_exists.sh: DM test - Verify reboot file '$reboot_file_path' exists"

[ -e "$reboot_file_path" ] &&
    log "dm/dm_verify_reboot_file_exists.sh: reboot file exists in $reboot_file_path - Success" ||
    raise "reboot file is missing - $reboot_file_path" -l "dm/dm_verify_reboot_file_exists.sh" -tc
[ -s "$reboot_file_path" ] &&
    log "dm/dm_verify_reboot_file_exists.sh: reboot file is not empty - $reboot_file_path - Success" ||
    raise "reboot file is empty - $reboot_file_path" -l "dm/dm_verify_reboot_file_exists.sh" -tc

cat $reboot_file_path | grep -q "REBOOT"
if [ $? = 0 ]; then
    log "dm/dm_verify_reboot_file_exists.sh: 'REBOOT' string found in file $reboot_file_path"
    reason=$(cat $reboot_file_path | awk '{print $2}')
    log "dm/dm_verify_reboot_file_exists.sh: Found reason: $reason"
else
    raise "Could not find REBOOT string in file $reboot_file_path" -l "dm/dm_verify_reboot_file_exists.sh" -tc
fi

pass
