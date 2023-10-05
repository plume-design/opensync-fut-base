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
tools/device/check_wpa3_compatibility.sh [-h] arguments
Description:
    - Script checks device WPA3 compatibility
Arguments:
    -h  show this help message
Script usage example:
    ./tools/device/check_wpa3_compatibility.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_wpa3_compatibility
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
    log "tools/device/check_wpa3_compatibility.sh: WPA3 compatible"
    exit 0
else
    log "tools/device/check_wpa3_compatibility.sh: WPA3 incompatible"
    raise "WPA3 is not compatible on device" -l "tools/device/check_wpa3_compatibility.sh" -s
fi
