#!/bin/sh

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
tools/device/device_init.sh [-h] arguments
Description:
    - This script returns the device into a default state, that should be equal to the state right after boot.
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/device_init.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "tools/device/device_init.sh: Device Default Initialization"

device_init &&
    log -deb "tools/device/device_init.sh Success: device_init" ||
    raise "Failed: device_init" -l "tools/device/device_init.sh" -ds

restart_managers
log -deb "tools/device/device_init.sh: Executed restart_managers, exit code: $?"

for if_name in "$@"
    do
        wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is if_name "$if_name" &&
            log -deb "tools/device/device_init.sh - Wifi_Radio_State::if_name '$if_name' present - Success" ||
            raise "Wifi_Radio_State::if_name for '$if_name' does not exist" -l "tools/device/device_init.sh" -ds
    done

exit 0
