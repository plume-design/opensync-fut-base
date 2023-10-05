#!/bin/sh

source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
ltem/ltem_setup.sh [-h] arguments
Description:
    - Setup device for LTEM testing
Arguments:
    -h : show this help message
    \$1 (lte_if_name)          : lte interface name    : (string)(required)
    \$2 (access_point_name)    : SIM Access Point Name : (string)(required)
    \$3 (os_persist)           : os persist            : (bool)(required)
Script usage example:
    ./ltem/ltem_setup.sh wwan0 data.icore.name true
    ./ltem/ltem_setup.sh wwan0 data.icore.name false
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_MANAGER_LTEM" "y" ||
    raise "CONFIG_MANAGER_LTEM != y - LTEM is not present on the device" -l "ltem/ltem_setup.sh" -s

NARGS=3
[ $# -ne ${NARGS} ] &&
    raise "ltem/ltem_setup.sh requires ${NARGS} input argument(s), $# given" -arg

if_name=${1}
apn=${2}
os_persist=${3}

device_init &&
    log -deb "ltem/ltem_setup.sh - Device initialized - Success" ||
    raise "FAIL: Could not initialize device: device_init" -l "ltem/ltem_setup.sh" -ds

start_openswitch &&
    log -deb "ltem/ltem_setup.sh - OpenvSwitch started - Success" ||
    raise "FAIL: Could not start OpenvSwitch: start_openswitch" -l "ltem/ltem_setup.sh" -ds

restart_managers
log -deb "ltem/ltem_setup.sh: Executed restart_managers, exit code: $?"

empty_ovsdb_table AW_Debug &&
    log -deb "ltem/ltem_setup.sh - AW_Debug table emptied - Success" ||
    raise "FAIL: empty_ovsdb_table AW_Debug - Could not empty AW_Debug table" -l "ltem/ltem_setup.sh" -ds

set_manager_log LTEM TRACE &&
    log -deb "ltem/ltem_setup.sh - Manager log for SM set to TRACE - Success" ||
    raise "FAIL: set_manager_log SM TRACE - Could not set manager log severity" -l "ltem/ltem_setup.sh" -ds

check_ovsdb_table_exist Lte_Config &&
    log -deb "ltem/ltem_setup.sh - Lte_Config table exists in OVSDB - Success" ||
    raise "FAIL: Lte_Config table does not exist in OVSDB" -l "ltem/ltem_setup.sh" -s

check_field=$(${OVSH} s Lte_Config -w if_name==$if_name)
if [ -z "$check_field" ]; then
    insert_ovsdb_entry Lte_Config -w if_name "$if_name" -i if_name "$if_name" \
        -i manager_enable "true" \
        -i lte_failover_enable "true" \
        -i ipv4_enable "true" \
        -i modem_enable "true" \
        -i force_use_lte "false" \
        -i apn "$apn" \
        -i report_interval "60" \
        -i active_simcard_slot "0" \
        -i os_persist "$os_persist" &&
            log -deb "ltem/ltem_setup.sh - Lte_Config::lte interface $if_name was inserted - Success" ||
            raise "FAIL: Lte_Config::lte interface $if_name is not inserted" -l "ltem/ltem_setup.sh" -ds
else
    log -deb "ltem/ltem_setup.sh - Entry for $if_name in Lte_Config already exists, skipping..."
fi

check_field=$(${OVSH} s Wifi_Inet_Config -w if_name==$if_name)
if [ -z "$check_field" ]; then
    insert_ovsdb_entry Wifi_Inet_Config -w if_name "$if_name" -i if_name "$if_name" \
        -i if_type "lte" \
        -i ip_assign_scheme "dhcp" \
        -i enabled "true" \
        -i network "true" \
        -i NAT "true" \
        -i os_persist "$os_persist" &&
            log -deb "ltem/ltem_setup.sh - Insert entry for $if_name interface in Wifi_Inet_Config - Success" ||
            raise "FAIL: Insert was not done for the entry of $if_name interface in Wifi_Inet_Config " -l "ltem/ltem_setup.sh" -ds
else
    log -deb "ltem/ltem_setup.sh - Entry for $if_name in Wifi_Inet_Config already exists, skipping..."
fi
