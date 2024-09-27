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
tools/device/check_kconfig_option.sh [-h] arguments
Description:
    - Script checks device Kconfig option value
    - If kconfig_option value is equal to kconfig_value script returns exit code 0
    - If kconfig_option value is not equal to kconfig_value script returns exit code 1
Arguments:
    -h  show this help message
    - \$1 (kconfig_option) : Kconfig option to check : (string)(required)
    - \$2 (kconfig_value)  : Kconfig value to check  : (string)(required)
Script usage example:
    ./tools/device/check_kconfig_option.sh CONFIG_MANAGER_WM y
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
kconfig_option=${1}
kconfig_value=${2}

check_kconfig_option "${kconfig_option}" "${kconfig_value}"
