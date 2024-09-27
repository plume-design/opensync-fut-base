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
onbrd/onbrd_verify_dhcp_dry_run_success.sh [-h] arguments
Description:
    - Validate dhcp dry run was successful.
    - Connection_Manager_Uplink::has_L3 is true indicating the OFFER message from DHCP server was received.
Arguments:
    -h  show this help message
    \$1 (if_name) : Used to define WAN interface : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./onbrd/onbrd_verify_dhcp_dry_run_success.sh <IF-NAME>
Script usage example:
    ./onbrd/onbrd_verify_dhcp_dry_run_success.sh eth0
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Connection_Manager_Uplink
    set_interface_up "$if_name" || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

check_kconfig_option "TARGET_CAP_EXTENDER" "y" ||
    raise "TARGET_CAP_EXTENDER != y - Testcase applicable only for EXTENDER-s" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -s

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -arg
if_name=$1

log_title "onbrd/onbrd_verify_dhcp_dry_run_success.sh: ONBRD test - Verify DHCP dry run success"

log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Checking if WANO is enabled, if yes, skip..."
check_kconfig_option "CONFIG_MANAGER_WANO" "y" &&
    raise "WANO manager is enabled, skipping test!" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -s

# Toggling the uplink interface DOWN/UP
log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Dropping interface $if_name"
set_interface_down "$if_name" &&
    log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Interface $if_name is down - Success" ||
    raise "Could not bring down interface $if_name" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -ds

log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Waiting for Connection_Manager_Uplink::has_L2 is false on $if_name"
wait_ovsdb_entry Connection_Manager_Uplink -w if_name "$if_name" -is has_L2 false &&
    log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: wait_ovsdb_entry - Interface $if_name has_L2 is false - Success" ||
    raise "wait_ovsdb_entry - Connection_Manager_Uplink::has_L2 is not false" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -tc

log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Bringing up interface $if_name"
set_interface_up "$if_name" &&
    log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Interface $if_name is up - Success" ||
    raise "Could not bring up interface $if_name" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -ds

log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Waiting for Connection_Manager_Uplink::has_L2 is true on $if_name"
wait_ovsdb_entry Connection_Manager_Uplink -w if_name "$if_name" -is has_L2 true &&
    log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: wait_ovsdb_entry - Connection_Manager_Uplink::has_L2 is 'true' - Success" ||
    raise "wait_ovsdb_entry - Connection_Manager_Uplink::has_L2 is not 'true'" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -tc

log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: Waiting for Connection_Manager_Uplink::has_L3 is true on $if_name"
wait_ovsdb_entry Connection_Manager_Uplink -w if_name "$if_name" -is has_L3 true &&
    log "onbrd/onbrd_verify_dhcp_dry_run_success.sh: wait_ovsdb_entry - Connection_Manager_Uplink::has_L3 is 'true' - Success" ||
    raise "wait_ovsdb_entry - Connection_Manager_Uplink::has_L3 is not 'true'" -l "onbrd/onbrd_verify_dhcp_dry_run_success.sh" -tc

pass
