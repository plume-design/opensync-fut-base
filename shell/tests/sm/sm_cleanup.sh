#!/bin/sh

# Clean up after tests for SM.

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

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
