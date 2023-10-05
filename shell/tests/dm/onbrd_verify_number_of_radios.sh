#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_number_of_radios.sh [-h] arguments
Description:
    - Validate number of radios on device
Arguments:
    -h  show this help message
    \$1 (num_of_radios) : used as number of radios to verify correct number of radios configured : (int)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_number_of_radios.sh <NUM-OF-RADIOS>
Script usage example:
    ./onbrd/onbrd_verify_number_of_radios.sh 2
    ./onbrd/onbrd_verify_number_of_radios.sh 3
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
print_tables Wifi_Radio_State
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_number_of_radios.sh" -arg
num_of_radios=$1

log_title "onbrd/onbrd_verify_number_of_radios.sh: ONBRD test - Verify number of radios"

log "onbrd/onbrd_verify_number_of_radios.sh: Verify number of radios, waiting for '${num_of_radios}'"
wait_for_function_response 0 "check_number_of_radios $num_of_radios" &&
    log "onbrd/onbrd_verify_number_of_radios.sh: Number of radios is $num_of_radios - Success" ||
    raise "FAIL: Number of radios is not $num_of_radios" -l "onbrd/onbrd_verify_number_of_radios.sh" -tc

pass
