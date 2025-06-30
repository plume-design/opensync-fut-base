#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
tools/device/restart_opensync.sh [-h] arguments
Description:
    - Restarts opensync on the device
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/restart_opensync.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log "tools/device/restart_opensync.sh: Restarting OpenSync"
restart_managers
log -deb "tools/device/restart_opensync.sh: Executed restart_managers, exit code: $?"
