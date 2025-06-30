#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

dm_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
dm/dm_verify_no_reboot.sh [-h]
Description:
    - The script verifies the functionality of the deferred reboot when `module_name` is performing a critical task.
Arguments:
    -h  show this help message
Testcase procedure:
    - On DEVICE: Run: ./${dm_setup_file} (see ${dm_setup_file} -h)
    - On DEVICE: Run: ./dm/dm_verify_no_reboot.sh
Script usage example:
    ./dm/dm_verify_no_reboot.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

no_reboot_dir_path=$(get_kconfig_option_value "CONFIG_NO_REBOOT_DIR" | tr -d '"' "'")
[ -z ${no_reboot_dir_path} ] && raise "Kconfig option CONFIG_NO_REBOOT_DIR has no value" -l "dm/dm_verify_no_reboot.sh" -arg

log_title "dm/dm_verify_no_reboot.sh: DM test - Verify no_reboot in directory ${no_reboot_dir_path}"

set_no_reboot_init_state() {
    [ -n ${no_reboot_dir_path} ] && rm -rf ${no_reboot_dir_path}/*
    remove_ovsdb_entry Node_State -w module "no_reboot"
}

trap '
    fut_ec=$?
    print_tables Node_State
    ls -la ${no_reboot_dir_path} || true
    set_no_reboot_init_state
    trap - EXIT INT
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

set_no_reboot_init_state

# Set no_reboot with voip
log "dm/dm_verify_no_reboot.sh: set no_reboot with voip"
${OPENSYNC_ROOTDIR}/bin/dm --no-reboot --set voip

# Verify file ${no_reboot_dir_path}/voip exists
[ -f ${no_reboot_dir_path}/voip ] &&
    log "dm/dm_verify_no_reboot.sh: file ${no_reboot_dir_path}/voip exists - Success" ||
    raise "file ${no_reboot_dir_path}/voip does not exist" -l "dm/dm_verify_no_reboot.sh" -tc

# Verify Node_State module/key/value is no_reboot/no_reboot/true
check_ovsdb_entry Node_State -w key "no_reboot" -w module "no_reboot" -w value \"true\" &&
    log "dm/dm_verify_no_reboot.sh: Node_State key==no_reboot module==no_reboot value==true - Success" ||
    raise "Node_State is not key==no_reboot module==no_reboot value==true" -l "dm/dm_verify_no_reboot.sh" -tc

# Set no_reboot with "another_critical_app"
log "dm/dm_verify_no_reboot.sh: set no_reboot with another_critical_app"
${OPENSYNC_ROOTDIR}/bin/dm --no-reboot --set another_critical_app

# Verify file ${no_reboot_dir_path}/another_critical_app exists
[ -f ${no_reboot_dir_path}/another_critical_app ] &&
    log "dm/dm_verify_no_reboot.sh: file ${no_reboot_dir_path}/another_critical_app exists - Success" ||
    raise "file ${no_reboot_dir_path}/another_critical_app does not exist" -l "dm/dm_verify_no_reboot.sh" -tc

# Verify Node_State module no_reboot value remained true
check_ovsdb_entry Node_State -w key "no_reboot" -w module "no_reboot" -w value \"true\" &&
    log "dm/dm_verify_no_reboot.sh: Node_State key==no_reboot module==no_reboot value==true - Success" ||
    raise "Node_State is not key==no_reboot module==no_reboot value==true" -l "dm/dm_verify_no_reboot.sh" -tc

# Clear no_reboot with "another_critical_app"
log "dm/dm_verify_no_reboot.sh: clear no_reboot with another-critical-app while voip is still active"
${OPENSYNC_ROOTDIR}/bin/dm --no-reboot --clear another_critical_app

# Verify file ${no_reboot_dir_path}/another_critical_app does not exist anymore
[ ! -f ${no_reboot_dir_path}/another_critical_app ] &&
    log "dm/dm_verify_no_reboot.sh: file ${no_reboot_dir_path}/another_critical_app does not exist anymore - Success" ||
    raise "file ${no_reboot_dir_path}/another_critical_app still exists even though it should not" -l "dm/dm_verify_no_reboot.sh" -tc

# Verify Node_State module no_reboot value remained true
check_ovsdb_entry Node_State -w key "no_reboot" -w module "no_reboot" -w value \"true\" &&
    log "dm/dm_verify_no_reboot.sh: Node_State key==no_reboot module==no_reboot value==true - Success" ||
    raise "Node_State is not key==no_reboot module==no_reboot value==true" -l "dm/dm_verify_no_reboot.sh" -tc

# Clear no_reboot with voip
log "dm/dm_verify_no_reboot.sh: clear no_reboot with voip - no other critical app active"
${OPENSYNC_ROOTDIR}/bin/dm --no-reboot --clear voip

# Verify file ${no_reboot_dir_path}/voip does not exist anymore
[ ! -f ${no_reboot_dir_path}/voip ] &&
    log "dm/dm_verify_no_reboot.sh: file ${no_reboot_dir_path}/voip does not exist anymore - Success" ||
    raise "file ${no_reboot_dir_path}/voip still exists even though it should not" -l "dm/dm_verify_no_reboot.sh" -tc

# Verify that ${no_reboot_dir_path} directory is empty again
[ -z "$(ls -A ${no_reboot_dir_path}/)" ] &&
    log "dm/dm_verify_no_reboot.sh: no_reboot directory $no_reboot_dir_path is empty again - Success" ||
    raise "no_reboot directory $no_reboot_dir_path is not empty" -l "dm/dm_verify_no_reboot.sh" -tc

# verify Node_State module no_reboot value changed to false
check_ovsdb_entry Node_State -w key "no_reboot" -w module "no_reboot" -w value \"false\" &&
    log "dm/dm_verify_no_reboot.sh: Node_State key==no_reboot module==no_reboot value==false - Success" ||
    raise "Node_State is not key==no_reboot module==no_reboot value==false" -l "dm/dm_verify_no_reboot.sh" -tc


pass
