#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"

cm_setup_file="cm2/cm2_setup.sh"
adr_router_man_file="tools/server/cm/address_router_man.sh"
arping_router_man_file="tools/server/cm/arping_man.sh"
step_1_name="router_blocked"
step_2_name="router_unblocked"

usage()
{
cat << usage_string
cm2/cm2_network_outage_router.sh [-h] arguments
Description:
    - Test script validates Uplink_Events behaviour in case of router loss
Arguments:
    -h : show this help message
    \$1 (test_step) : used as test step : (string)(required) : (${step_1_name}, ${step_2_name})
Testcase procedure:
    - On DEVICE: Run: ${cm_setup_file} ${step_1_name} (see ${cm_setup_file} -h)
    - On RPI SERVER: Run: ${adr_router_man_file} <WAN-IP-ADDRESS> block
    - On RPI SERVER: Run: ${arping_router_man_file} <WAN-IP-ADDRESS> block
    - On DEVICE: Run: ${cm_setup_file} ${step_2_name} (see ${cm_setup_file} -h)
    - On RPI SERVER: Run: ${adr_router_man_file} <WAN-IP-ADDRESS> unblock
    - On RPI SERVER: Run: ${arping_router_man_file} <WAN-IP-ADDRESS> unblock
Script usage example:
    ./cm2/cm2_network_outage_router.sh ${step_1_name}
    ./cm2/cm2_network_outage_router.sh ${step_2_name}
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CM2_USE_STABILITY_CHECK" "y" ||
    raise "CM2_USE_STABILITY_CHECK != y - Testcase applicable only for CONFIG_CM2_USE_STABILITY_CHECK" -l "cm2/cm2_network_outage_router.sh" -s

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires at exactly ${NARGS} input argument(s)" -l "cm2/cm2_network_outage_router.sh" -arg
test_step=${1}

trap '
    fut_rc=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Uplink_Events
    fut_info_dump_line
    exit $fut_rc
' EXIT INT TERM

log_title "cm2/cm2_network_outage_router.sh: CM2 test - Network Outage for router failures"

case $test_step in
    ${step_1_name})
        ovsh d Uplink_Events
        log "cm2/cm2_network_outage_router.sh: Waiting for disconnection Uplink_Events on $if_name"
        wait_ovsdb_entry Uplink_Events -t 300 -w type IPALL_ROUTER -is connected false &&
            log "cm2/cm2_network_outage_router.sh: wait_ovsdb_entry - Uplink_Events has IPALL_ROUTER disconnection event - Success" ||
            raise "No IPALL_ROUTER disconnection event in Uplink_Events detected." -l "cm2/cm2_network_outage_router.sh" -fc
    ;;
    ${step_2_name})
        log "cm2/cm2_network_outage_router.sh: Waiting for connection Uplink_Events on $if_name"
        uuid=$(ovsh s Uplink_Events -w connected==false _uuid -U -r)
        wait_ovsdb_entry Uplink_Events -t 300 -w type IPALL_ROUTER -wn _uuid $uuid -is connected true &&
            log "cm2/cm2_network_outage_router.sh: wait_ovsdb_entry - Uplink_Events has IPALL_ROUTER connection event - Success" ||
            raise "No IPALL_ROUTER connection event in Uplink_Event detected." -l "cm2/cm2_network_outage_router.sh" -fc
    ;;
    *)
        raise "Incorrect test_step provided" -l "cm2/cm2_network_outage_router.sh" -arg
esac

pass
