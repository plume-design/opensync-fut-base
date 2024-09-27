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
tools/device/check_ht_mode_at_os_level.sh [-h] arguments
Description:
    - Script runs unit_lib::check_ht_mode_at_os_level with given parameters
Arguments:
    -h  show this help message
    - \$1  (ht_mode)        :HT mode                :(string, required)
    - \$2  (vif_if_name)    :VIF interface name     :(string, required)
    - \$3  (channel)        :channel                :(int, required)
Script usage example:
    ./tools/device/check_ht_mode_at_os_level.sh HT40 home-ap-24 2
See unit_lib_lib::check_ht_mode_at_os_level for more information
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/check_ht_mode_at_os_level.sh" -arg

trap '
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State
    fut_info_dump_line
' EXIT INT TERM

ht_mode=${1}
vif_if_name=${2}
channel=${3}

log "tools/device/check_ht_mode_at_os_level.sh: Checking ht_mode at system level - LEVEL2"
check_ht_mode_at_os_level "$ht_mode" "$vif_if_name" "$channel" &&
    log "tools/device/check_ht_mode_at_os_level.sh: LEVEL2 - check_ht_mode_at_os_level - ht_mode $ht_mode set at system level - Success" ||
    raise "LEVEL2 - check_ht_mode_at_os_level - ht_mode  $ht_mode not set at system level" -l "tools/device/check_ht_mode_at_os_level.sh" -tc

pass
