#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
sm/sm_setup.sh [-h] arguments
Description:
    - Setup device for SM testing
Arguments:
    -h : show this help message
    \$@ (radio_if_names) : wait for if_name in Wifi_Radio_State table to be present after setup : (string)(optional)
Script usage example:
    ./sm/sm_setup.sh
    ./sm/sm_setup.sh wifi0 wifi1
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac
check_kconfig_option "CONFIG_MANAGER_SM" "y" ||
    raise "CONFIG_MANAGER_SM != y - SM not present on device" -l "sm/sm_setup.sh" -s

if check_kconfig_option "CONFIG_MANAGER_OWM" "y"; then
    if [ "$(get_ovsdb_entry_value Node_Services status -w service owm)" == "enabled" ]; then
        wireless_manager=owm
    elif [ "$(get_ovsdb_entry_value Node_Services status -w service wm)" == "enabled" ]; then
        wireless_manager=wm
    else
        raise "FAIL: No OpenSync wireless manager enabled on the device" -l "sm/sm_setup.sh" -ds
    fi
elif [ "$(get_ovsdb_entry_value Node_Services status -w service wm)" == "enabled" ]; then
    wireless_manager=wm
else
    raise "FAIL: WM disabled on the device" -l "sm/sm_setup.sh" -ds
fi

log "sm/sm_setup.sh - OpenSync wireless manager '${wireless_manager}' is enabled on the device - Success"
export FUT_OS_WIRELESS_MGR_LC="${wireless_manager}"
export FUT_OS_WIRELESS_MGR_UC="$(echo ${wireless_manager:?} | awk '{print toupper($0)}')"

device_init &&
    log -deb "sm/sm_setup.sh - Device initialized - Success" ||
    raise "FAIL: device_init - Could not initialize device" -l "sm/sm_setup.sh" -ds

start_openswitch &&
    log -deb "sm/sm_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: start_openswitch - Could not start OpenvSwitch" -l "sm/sm_setup.sh" -ds

start_wireless_driver &&
    log -deb "sm/sm_setup.sh - Wireless driver started - Success" ||
    raise "FAIL: start_wireless_driver - Could not start wireless driver" -l "sm/sm_setup.sh" -ds

restart_managers
log -deb "sm/sm_setup.sh - Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "sm/sm_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "sm/sm_setup.sh" -ds

set_manager_log ${FUT_OS_WIRELESS_MGR_UC:?} TRACE &&
    log -deb "sm/sm_setup.sh - Manager log for ${FUT_OS_WIRELESS_MGR_UC:?} set to TRACE - Success" ||
    raise "FAIL: set_manager_log ${FUT_OS_WIRELESS_MGR_UC:?} TRACE - Could not set manager log severity" -l "sm/sm_setup.sh" -ds

set_manager_log SM TRACE &&
    log -deb "sm/sm_setup.sh - Manager log for SM set to TRACE - Success" ||
    raise "FAIL: set_manager_log SM TRACE - Could not set manager log severity" -l "sm/sm_setup.sh" -ds

vif_reset &&
    log -deb "sm/sm_setup.sh - vif_reset - Success" ||
    raise "FAIL: vif_reset - Could not reset VIFs" -l "sm/sm_setup.sh" -ow

for if_name in "$@"
do
    wait_ovsdb_entry Wifi_Radio_State -w if_name "$if_name" -is if_name "$if_name" &&
        log -deb "sm/sm_setup.sh - Wifi_Radio_State::if_name '$if_name' present - Success" ||
        raise "FAIL: Wifi_Radio_State::if_name for '$if_name' does not exist" -l "sm/sm_setup.sh" -ds
done
