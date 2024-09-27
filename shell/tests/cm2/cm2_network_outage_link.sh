#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"

cm_setup_file="cm2/cm2_setup.sh"
usage()
{
cat << usage_string
cm2/cm2_network_outage_link.sh [-h] arguments
Description:
    - Test script validates Uplink_Events behaviour in case of link loss
Arguments:
    -h : show this help message
    \$1 (if_name) : used as L2 interface : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${cm_setup_file} (see ${cm_setup_file} -h)
                 Run: ./cm2/cm2_network_outage_link.sh <IF-NAME-L2>
Script usage example:
    ./cm2/cm2_network_outage_link.sh eth0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

check_kconfig_option "CM2_USE_STABILITY_CHECK" "y" ||
    raise "CM2_USE_STABILITY_CHECK != y - Testcase applicable only for CONFIG_CM2_USE_STABILITY_CHECK" -l "cm2/cm2_network_outage_link.sh" -s

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires at exactly ${NARGS} input argument(s)" -l "cm2/cm2_network_outage_link.sh" -arg
if_name=$1

trap '
    fut_rc=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Uplink_Events
    set_interface_up "$if_name" || true
    fut_info_dump_line
    exit $fut_rc
' EXIT INT TERM

log_title "cm2/cm2_network_outage_link.sh: CM2 test - Network Outage for link failures"

log "cm2/cm2_network_outage_link.sh: Clear Uplink_Events table"
ovsh d Uplink_Events

log "cm2/cm2_network_outage_link.sh: Dropping interface $if_name"
set_interface_down "$if_name" &&
    log "cm2/cm2_network_outage_link.sh: Interface $if_name is down - Success" ||
    raise "Could not bring down interface $if_name" -l "cm2/cm2_network_outage_link.sh" -ds

log "cm2/cm2_network_outage_link.sh: Waiting for disconnection Uplink_Events on $if_name"
wait_ovsdb_entry Uplink_Events -w type LINK -is connected false &&
    log "cm2/cm2_network_outage_link.sh: wait_ovsdb_entry - Uplink_Events has LINK disconnection event - Success" ||
    raise "No LINK disconnection event in Uplink_Events detected." -l "cm2/cm2_network_outage_link.sh" -fc

# wait_ovsdb_entry needs to use uuid of old entry as != otherwise the new entry is not detected
uuid=$(ovsh s Uplink_Events -w connected==false _uuid -U -r)

log "cm2/cm2_link_lost.sh: Bringing up interface $if_name"
set_interface_up "$if_name" &&
    log "cm2/cm2_link_lost.sh: Interface $if_name is up - Success" ||
    raise "Could not bring up interface $if_name" -l "cm2/cm2_link_lost.sh" -ds

log "cm2/cm2_network_outage_link.sh: Waiting for connection Uplink_Events on $if_name"
wait_ovsdb_entry Uplink_Events -w type LINK -wn _uuid $uuid -is connected true &&
    log "cm2/cm2_network_outage_link.sh: wait_ovsdb_entry - Uplink_Events has LINK connection event - Success" ||
    raise "No LINK connection event in Uplink_Event detected." -l "cm2/cm2_network_outage_link.sh" -fc

pass
