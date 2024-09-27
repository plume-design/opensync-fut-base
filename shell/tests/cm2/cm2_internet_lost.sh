#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

cm_setup_file="cm2/cm2_setup.sh"
addr_internet_man_file="tools/server/cm/address_internet_man.sh"
step_1_name="check_counter"
step_2_name="internet_recovered"
counter_default=4
usage()
{
cat << usage_string
cm2/cm2_internet_lost.sh [-h] arguments
Description:
    - Script checks if CM updates Connection_Manager_Uplink field 'unreachable_internet_counter' reaches given value when internet is unreachable
      If the field 'unreachable_internet_counter' doesen't reach given value, test fails
Arguments:
    -h : show this help message
    \$1 (if_name)                      : WAN interface name               : (string)(required)
    \$2 (unreachable_internet_counter) : used as value counter must reach : (int)(optional)    : (default:${counter_default})
    \$3 (test_step)                    : used as test step                : (string)(optional) : (default:${step_1_name}) : (${step_1_name}, ${step_2_name})
Testcase procedure:
    - On DEVICE: Run: ./${cm_setup_file} (see ${cm_setup_file} -h)
                 Run: ./cm2/cm2_internet_lost.sh <WAN_IF_NAME> <UNRCH-CLOUD-COUNTER> ${step_1_name}
    - On RPI SERVER: Run: ./${addr_internet_man_file} <WAN-IP-ADDRESS> block
    - On DEVICE: Run: ./cm2/cm2_internet_lost.sh <WAN_IF_NAME> <UNRCH-CLOUD-COUNTER> ${step_2_name}
    - On RPI SERVER: Run: ./${addr_internet_man_file} <WAN-IP-ADDRESS> unblock
Script usage example:
    ./cm2/cm2_internet_lost.sh eth0 ${counter_default} ${step_1_name}
    ./cm2/cm2_internet_lost.sh eth0 0 ${step_2_name}
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "TARGET_CAP_EXTENDER" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Testcase applicable only for EXTENDER-s" -l "cm2/cm2_internet_lost.sh" -s

NARGS=1
[ $# -lt ${NARGS} ] && usage && raise "Requires at least ${NARGS} input argument(s)" -l "cm2/cm2_internet_lost.sh" -arg
if_name=${1}
unreachable_internet_counter=${2:-${counter_default}}
test_type=${3:-"${step_1_name}"}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Connection_Manager_Uplink
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "cm2/cm2_internet_lost.sh: CM2 test - Internet Lost - $test_type"

if [ "$test_type" = "${step_1_name}" ]; then
    log "cm2/cm2_internet_lost.sh: Waiting for unreachable_internet_counter to reach $unreachable_internet_counter"
    wait_ovsdb_entry Connection_Manager_Uplink -w if_name "${if_name}" -is unreachable_internet_counter "$unreachable_internet_counter" &&
        log "cm2/cm2_internet_lost.sh: Connection_Manager_Uplink::unreachable_internet_counter is $unreachable_internet_counter - Success" ||
        raise "Connection_Manager_Uplink::unreachable_internet_counter is not $unreachable_internet_counter" -l "cm2/cm2_internet_lost.sh" -fc
elif [ "$test_type" = "${step_2_name}" ]; then
    log "cm2/cm2_internet_lost.sh: Waiting for unreachable_internet_counter to reset to 0"
    wait_ovsdb_entry Connection_Manager_Uplink -w if_name "${if_name}" -is unreachable_internet_counter "0" &&
        log "cm2/cm2_internet_lost.sh: Connection_Manager_Uplink::unreachable_internet_counter reset to 0 - Success" ||
        raise "Connection_Manager_Uplink::unreachable_internet_counter is not 0" -l "cm2/cm2_internet_lost.sh" -fc
else
    raise "Wrong test type option" -l "cm2/cm2_internet_lost.sh" -arg
fi

pass
