#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

dm_setup_file="dm/dm_setup.sh"
usage()
{
cat << usage_string
tools/device/reboot_dut_w_reason.sh [-h]
Description:
    Script reboots device in a configured manner:
      - USER intervention and
      - CLOUD reboot currently supported.
Arguments:
    -h  show this help message
    \$1 (reboot_reason) : Reboot trigger type             : (string)(required)
    Optional argument (If reboot reason is 'CLOUD'):
    \$2 (opensync_path) : Path to Opensync root directory : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${dm_setup_file} (see ${dm_setup_file} -h)
    - On DEVICE: Run: .tools/device/reboot_dut_w_reason.sh <REBOOT_REASON>
Script usage example:
    .tools/device/reboot_dut_w_reason.sh USER
    .tools/device/reboot_dut_w_reason.sh CLOUD /usr/opensync
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CONFIG_OSP_REBOOT_PSTORE" "y" ||
    raise "CONFIG_OSP_REBOOT_PSTORE != y - Testcase not applicable REBOOT PERSISTENT STORAGE not supported" -l "tools/device/reboot_dut_w_reason.sh" -s

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "tools/device/reboot_dut_w_reason.sh" -arg
reboot_reason=$1
if [ $reboot_reason == "CLOUD" ]; then
    NARGS=2
    [ $# -eq ${NARGS} ] && opensync_path=$2 ||
    raise "Invalid/missing argument - path to opensync root directory" -l "tools/device/reboot_dut_w_reason.sh" -arg
fi

log_title "tools/device/reboot_dut_w_reason.sh: DM test - Reboot DUT with reason - $reboot_reason"

log "tools/device/reboot_dut_w_reason.sh - Simulating $reboot_reason reboot"
case "$reboot_reason" in
    "USER")
        reboot
    ;;
    "CLOUD")
        trigger_cloud_reboot ${opensync_path}
        print_tables Wifi_Test_Config
    ;;
    *)
        raise "Unknown reason to check: $reboot_reason" -l "tools/device/reboot_dut_w_reason.sh" -arg
    ;;
esac

pass
