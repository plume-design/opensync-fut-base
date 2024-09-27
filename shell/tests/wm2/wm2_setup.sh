#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
wm2/wm2_setup.sh [-h] arguments
Description:
    - Setup device for Wireless Manager testing
Arguments:
    -h : show this help message
    \$1 (wireless_manager_name) : provide the name of the wireless manager : (string)(optional)
    \$@ (radio_if_names)        : wait for if_name in Wifi_Radio_State table to be present after setup : (string)(optional)
Script usage example:
    ./wm2/wm2_setup.sh
    ./wm2/wm2_setup.sh wm
    ./wm2/wm2_setup.sh owm wifi0 wifi1
usage_string
}

trap '
    fut_ec=$?
    trap - EXIT INT
    if [ $fut_ec -ne 0 ]; then
        fut_info_dump_line
        print_tables Wifi_Radio_Config Wifi_Radio_State Wifi_VIF_Config Wifi_VIF_State
        fut_info_dump_line
    fi
    exit $fut_ec
' EXIT INT TERM

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

device_init &&
    log -deb "wm2/wm2_setup.sh - Device initialized - Success" ||
    raise "device_init - Could not initialize device" -l "wm2/wm2_setup.sh" -ds

empty_ovsdb_table AW_Debug &&
    log -deb "wm2/wm2_setup.sh - AW_Debug table emptied - Success" ||
    raise "empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "wm2/wm2_setup.sh" -ds

wireless_manager=${1:-"$(get_wireless_manager_name)"}
[ $# -ge 1 ] && shift

log "wm2/wm2_setup.sh - OpenSync wireless manager '${wireless_manager}' is enabled on the device - Success"
FUT_OS_WIRELESS_MGR_UC="$(echo ${wireless_manager:?} | awk '{print toupper($0)}')"

set_manager_log ${FUT_OS_WIRELESS_MGR_UC:?} TRACE &&
    log -deb "wm2/wm2_setup.sh - Manager log for ${FUT_OS_WIRELESS_MGR_UC:?} set to TRACE - Success" ||
    raise "set_manager_log ${FUT_OS_WIRELESS_MGR_UC:?} TRACE - Could not set manager log severity" -l "wm2/wm2_setup.sh" -ds

vif_reset &&
    log -deb "wm2/wm2_setup.sh - vif_reset - Success" ||
    raise "vif_reset - Could not reset VIFs" -l "wm2/wm2_setup.sh" -fc

for if_name in "$@"
do
    wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is if_name "$if_name" &&
        log -deb "wm2/wm2_setup.sh - Wifi_Radio_State::if_name '$if_name' present - Success" ||
        raise "Wifi_Radio_State::if_name for '$if_name' does not exist" -l "wm2/wm2_setup.sh" -ds
done
