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
brv/brv_is_bcm_license_on_system.sh [-h] arguments
Description:
    - Script checks if:
        1. BCM license is present on the system.
        2. License has support for services - OpenvSwitch HW acceleration
            and service queue needed for rate limiting.
Arguments:
    -h : show this help message
    \$1 (license_file) : BCM license with full path : (string)(required)
    \$2 (service) : Service support to be validated: (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${brv_setup_file} (see ${brv_setup_file} -h)
                 Run: ./brv/brv_is_bcm_license_on_system.sh <LICENSE-FILE> <SERVICE>
Script usage example:
    ./brv/brv_is_bcm_license_on_system.sh "/proc/driver/license" "FULL OVS"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires at exactly ${NARGS} input argument(s)" -l "brv/brv_is_bcm_license_on_system.sh" -arg
license_file=$1
service=$2

log_title "brv/brv_is_bcm_license_on_system.sh: BRV test - Check if license '${license_file}' is present on BCM device"

test -e "${license_file}"
if [ $? = 0 ]; then
    log "brv/brv_is_bcm_license_on_system.sh: License '${license_file}' found on device - Success"
else
    raise "License '${license_file}' could not be found on device" -l "brv/brv_is_bcm_license_on_system.sh" -tc
fi

cat "${license_file}" | grep -w "${service}" &&
    log "brv/brv_is_bcm_license_on_system.sh: License '${license_file}' has support for '${service}' - Success" ||
    raise "License '${license_file}' does not have support for '${service}'" -l "brv/brv_is_bcm_license_on_system.sh" -tc

pass
