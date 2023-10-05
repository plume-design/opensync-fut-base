#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" &> /dev/null
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" &> /dev/null

usage()
{
cat << usage_string
tools/device/reset_sta_interface.sh [-h] arguments
Description:
    - Reset STA interface to default values
Arguments:
    -h  show this help message
    See wm2_lib::reset_sta_interface for more information
Script usage example:
    ./tools/device/reset_sta_interface.sh bhaul-sta-l50
usage_string
}

trap '
fut_ec=$?
fut_info_dump_line
print_tables Wifi_VIF_Config Wifi_VIF_State || true
check_restore_ovsdb_server
fut_info_dump_line
exit $fut_ec
' EXIT SIGINT SIGTERM


NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/reset_sta_interface.sh" -arg

log "tools/device/$(basename "$0"): reset_sta_interface - Configuring STA interface"
reset_sta_interface "$@" &&
    log "tools/device/$(basename "$0"): reset_sta_interface - Success" ||
    raise "reset_sta_interface - Failed" -l "tools/device/$(basename "$0")" -tc

exit 0
