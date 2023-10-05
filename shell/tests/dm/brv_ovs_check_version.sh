#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

brv_setup_file="brv/brv_setup.sh"
usage()
{
cat << usage_string
brv/brv_ovs_check_version.sh [-h] \$1
Description:
    - Script checks if OVS version is retrievable from the system, fails otherwise
Arguments:
    -h : show this help message
Testcase procedure:
    - On DEVICE: Run: ./${brv_setup_file} (see ${brv_setup_file} -h)
                 Run: ./brv/brv_ovs_check_version.sh
Usage:
    ./brv/brv_ovs_check_version.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log_title "brv/brv_ovs_check_version.sh: BRV test - Verify OVS version"

ovs_ver="$(get_ovs_version)"
[ "${?}" == 0 ] && [ -n "${ovs_ver}" ] &&
    log "brv/brv_ovs_check_version.sh: Retrieved OVS version: OVS Version: ${ovs_ver}" ||
    raise "Failed to retrieve OVS version from device" -l "brv/brv_ovs_check_version.sh" -tc

pass
