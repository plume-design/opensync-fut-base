#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="nm2/nm2_setup.sh"
usage()
{
cat << usage_string
nm2/nm2_set_dns.sh [-h] arguments
Description:
    - Script configures interfaces dns through Wifi_inet_Config 'dns' field and checks if it is propagated
      into Wifi_Inet_State table and to the system, fails otherwise
Arguments:
    -h  show this help message
    \$1 (if_name)       : field if_name in Wifi_Inet_Config table                 : (string)(required)
    \$2 (if_type)       : field if_type in Wifi_Inet_Config table                 : (string)(required)
    \$3 (primary_dns)   : primary entry for field dns in Wifi_Inet_Config table   : (string)(required)
    \$4 (secondary_dns) : secondary entry for field dns in Wifi_Inet_Config table : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_set_dns.sh <IF-NAME> <IF-TYPE> <PRIMARY-DNS> <SECONDARY-DNS>
Script usage example:
    ./nm2/nm2_set_dns.sh wifi0 vif 1.2.3.4 4.5.6.7
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=4
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_set_dns.sh" -arg
if_name=$1
if_type=$2
primary_dns=$3
secondary_dns=$4

trap '
    fut_info_dump_line
    print_tables Wifi_Inet_Config Wifi_Inet_State
    reset_inet_entry $if_name || true
    check_restore_management_access || true
    check_restore_ovsdb_server
    fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "nm2/nm2_set_dns.sh: NM2 test - Testing table Wifi_Inet_Config field dns"

log "nm2/nm2_set_dns.sh: Creating Wifi_Inet_Config entries for interface '$if_name'"
create_inet_entry \
    -if_name "$if_name" \
    -enabled true \
    -network true \
    -ip_assign_scheme static \
    -inet_addr 10.10.10.30 \
    -netmask "255.255.255.0" \
    -if_type "$if_type" &&
        log "nm2/nm2_set_dns.sh: Interface $if_name created - Success" ||
        raise "FAIL: Failed to create $if_name interface" -l "nm2/nm2_set_dns.sh" -ds

log "nm2/nm2_set_dns.sh: Setting DNS for '$if_name' to $primary_dns, $secondary_dns"
configure_custom_dns_on_interface "$if_name" "$primary_dns" "$secondary_dns" &&
    log "nm2/nm2_set_dns.sh: Custom DNS set on interface '$if_name' - Success" ||
    raise "FAIL: Failed to set custom DNS for interface '$if_name'" -l "nm2/nm2_set_dns.sh" -tc

log "nm2/nm2_set_dns.sh: Checking if primary DNS was properly applied to interface '$if_name' - LEVEL2"
wait_for_function_response 0 "check_resolv_conf $primary_dns" &&
    log "nm2/nm2_set_dns.sh: LEVEL2 - Primary DNS set in /tmp/resolv.conf - interface '$if_name' - Success" ||
    raise "FAIL: LEVEL2 - Primary DNS configuration NOT valid - interface '$if_name'" -l "nm2/nm2_set_dns.sh" -tc

log "nm2/nm2_set_dns.sh: Checking if secondary DNS was properly applied to interface '$if_name' - LEVEL2"
wait_for_function_response 0 "check_resolv_conf $secondary_dns" &&
    log "nm2/nm2_set_dns.sh: LEVEL2 - Secondary DNS set in /tmp/resolv.conf - interface '$if_name' - Success" ||
    raise "FAIL: LEVEL2 - Secondary DNS configuration NOT valid - interface '$if_name'" -l "nm2/nm2_set_dns.sh" -tc

pass
