#!/bin/sh

# It is important for this particular testcase to capture current time ASAP
time_now=$(date -u +"%s")

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
# shellcheck disable=SC1091
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="onbrd/onbrd_setup.sh"
usage()
{
cat << usage_string
onbrd/onbrd_verify_dut_system_time_accuracy.sh [-h] arguments
Description:
    - Validate device time is within real time threshold
    - It is important to compare timestamps to the same time zone: UTC is used internally!
Arguments:
    -h  show this help message
    \$1 (time_ref)      : format: seconds since epoch. Used to compare system time.    : (int)(required)
    \$2 (time_accuracy) : format: seconds. Allowed time deviation from reference time. : (int)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_dut_system_time_accuracy.sh <ACCURACY> <REFERENCE-TIME>
Script usage example:
    ./onbrd/onbrd_verify_dut_system_time_accuracy.sh 2 $(date --utc +\"%s\")
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

if [ $FUT_SKIP_L2 == 'true' ]; then
    raise "Flag to skip LEVEL2 testcases enabled, skipping execution." -l "onbrd/onbrd_verify_dut_system_time_accuracy.sh" -s
fi

NARGS=2
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_dut_system_time_accuracy.sh" -arg
time_ref=$1
time_accuracy=$2

log_title "onbrd/onbrd_verify_dut_system_time_accuracy.sh: ONBRD test - Verify DUT system time is within threshold of the reference"

# Timestamps in human readable format
time_ref_str=$(date -D @"${time_ref}")
time_now_str=$(date -D @"${time_now}")

time_ref_timestamp=$(date -D "${time_ref_str}" +%s)
time_now_timestamp=$(date -D "${time_now_str}" +%s)

# Calculate time difference and ensure absolute value
time_diff=$(( time_ref_timestamp - time_now_timestamp ))
if [ $time_diff -lt 0 ]; then
    time_diff=$(( -time_diff ))
fi

log "onbrd/onbrd_verify_dut_system_time_accuracy.sh: Checking time ${time_now_str} against reference ${time_ref_str}"
if [ $time_diff -le "$time_accuracy" ]; then
    log "onbrd/onbrd_verify_dut_system_time_accuracy.sh: Time difference ${time_diff}s is within ${time_accuracy}s - Success"
else
    log -err "onbrd/onbrd_verify_dut_system_time_accuracy.sh:\nDevice time: ${time_now_str} -> ${time_now_timestamp}\nReference time: ${time_ref_str} -> ${time_ref_timestamp}"
    raise "FAIL: Time difference ${time_diff}s is NOT within ${time_accuracy}s" -l "onbrd/onbrd_verify_dut_system_time_accuracy.sh" -tc
fi

pass
