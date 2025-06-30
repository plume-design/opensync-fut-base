#!/bin/sh

# Clean up after tests for SM.

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
sm/sm_cleanup.sh [-h] arguments
Description:
    - Script removes the Wifi_Stats_Config table.
Arguments:
    -h : show this help message
Script usage example:
    ./sm/sm_cleanup.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "sm/sm_cleanup.sh: Removing the Wifi_Stats_Config table"
remove_ovsdb_entry Wifi_Stats_Config &&
    log "sm/sm_cleanup.sh: Wifi_Stats_Config table removed - Success" ||
    log -err "sm/sm_cleanup.sh: Failed to remove the Wifi_Stats_Config table"

wait_ovsdb_entry_remove Wifi_Stats_Config &&
    log "sm/sm_cleanup.sh: Wifi_Stats_Config table removed - Success" ||
    log -err "sm/sm_cleanup.sh: Failed to remove the Wifi_Stats_Config table"

print_tables Wifi_Stats_Config

pass
