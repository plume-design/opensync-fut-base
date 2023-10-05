#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="dm/othr_setup.sh"
usage()
{
cat << usage_string
othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh [-h] arguments
Description:
    - Script verifies correct configuration of ookla speedtest feature on DUT.
Arguments:
    -h   show this help message
    \$1  (config_path) :  full path to the config file of speedtest server :   (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh <SPEEDTEST_CONFIG_PATH>
Script usage example:
    ./othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh http://config.speedtest.net/v1/embed/x340jwcv4nz2ou3r/config
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh" -arg
config_path=$1

log_title "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh: OTHR test - Verify configuration of ookla speedtest feature"

check_kconfig_option "CONFIG_3RDPARTY_OOKLA" "y" ||
    check_kconfig_option "CONFIG_SPEEDTEST_OOKLA" "y" ||
        raise "OOKLA not present on device" -l "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh" -s

ookla_bin="${OPENSYNC_ROOTDIR}/bin/ookla"
[ -e "$ookla_bin" ] &&
    log "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh: ookla speedtest binary is present on system - Success" ||
    raise "FAIL: Ookla speedtest binary is not present on system" -l "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh" -s

speed_test_result=$(${ookla_bin} --upload-conn-range=16 -fjson -c ${config_path} -f human-readable 2>/dev/null)
if [ $? -eq 0 ]; then
    log "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh: Speedtest process started with below details:"
    echo "$speed_test_result"
else
    raise "FAIL: Speedtest process not started" -l "othr/othr_verify_ookla_speedtest_sdn_endpoint_config.sh" -tc
fi

pass
