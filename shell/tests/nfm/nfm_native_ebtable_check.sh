#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"

usage()
{
cat << usage_string
nfm/nfm_native_ebtable_check.sh [-h] arguments
Description:
    - This script will create ebtables rules by configuring rules in the Netfilter table.
      The script also validates that the rules are configured on the device.
Arguments:
    -h : show this help message
    \$1 (netfilter_table_name)  : Netfilter table name                                          : (string)(required)
    \$2 (chain_name)            : chain to use (eg. INPUT, FORWARD etc.)                        : (string)(required)
    \$3 (table_name)            : table to use (filter, nat or broute)                          : (string)(required)
    \$4 (ebtable_rule)          : condition to be matched                                       : (string)(required)
    \$5 (ebtable_target)        : action to take when the rule match (ACCEPT, DROP, CONTINUE)   : (string)(required)
    \$6 (ebtable_priority)      : rule priority                                                 : (string)(required)
    \$7 (update_target)         : updated target value                                          : (string)(required)
Script usage example:
    ./nfm/nfm_setup.sh
    ./nfm/nfm_native_ebtable_check.sh sample_filter BROUTING broute "-d 60:b4:f7:fc:2d:44" DROP 1 ACCEPT
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=7
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s), $# given" -l "/nfm/nfm_native_ebtable_check.sh" -arg

netfilter_table_name="${1}"
chain_name="${2}"
table_name="${3}"
ebtable_rule="${4}"
ebtable_target="${5}"
ebtable_priority="${6}"
update_target="${7}"

log_title "/nfm/nfm_native_ebtable_check.sh: Configuring and validating ebtables rules"

log "/nfm/nfm_native_ebtable_check.sh: Configuring Netfilter table entry (name:${netfilter_table_name}, rule:"${ebtable_rule}", target:"${ebtable_target}")"
insert_ovsdb_entry Netfilter -i name "${netfilter_table_name}" \
    -i chain "${chain_name}" \
    -i enable "true" \
    -i protocol "eth" \
    -i table "${table_name}" \
    -i rule "${ebtable_rule}" \
    -i target "${ebtable_target}" \
    -i priority "${ebtable_priority}" &&
        log "/nfm/nfm_native_ebtable_check.sh: Configuring Netfilter table (name:${netfilter_table_name}, rule:"${ebtable_rule}", target:"${ebtable_target}") - Success" ||
        raise "Failed to configuring Netfilter table (name: ${netfilter_table_name}, rule:"${ebtable_rule}", target:"${ebtable_target}")" -l "/nfm/nfm_native_ebtable_check.sh" -tc

log "/nfm/nfm_native_ebtable_check.sh: Checking ebtables rule is configured on the device"
is_ebtables_rule_configured "${table_name}" "${chain_name}" "${ebtable_rule}" "${ebtable_target}"
    log "/nfm/nfm_native_ebtable_check.sh: ebtables rule is configured on the device - Success" ||
    raise "ebtables rule is not configured on the device" -l "/nfm/nfm_native_ebtable_check.sh" -tc

#updating the added rule in Netfilter Table
log "/nfm/nfm_native_ebtable_check.sh: Updating Netfilter table from target:"${ebtable_target}" to "${update_target}""
update_ovsdb_entry Netfilter -w name "${netfilter_table_name}" -u target "${update_target}" &&
    log "/nfm/nfm_native_ebtable_check.sh: Updating Netfilter table from target:"${ebtable_target}" to "${update_target}" - Success" ||
    raise "Failed updating Netfilter table from target:"${ebtable_target}" to "${update_target}"" -l "/nfm/nfm_native_ebtable_check.sh" -tc

log "/nfm/nfm_native_ebtable_check.sh: Checking ebtables rule is configured on the device"
is_ebtables_rule_configured "${table_name}" "${chain_name}" "${ebtable_rule}" "${update_target}" &&
    log "/nfm/nfm_native_ebtable_check.sh: ebtables rule is configured on the device - Success" ||
    raise "ebtables rule is not configured on the device" -l "/nfm/nfm_native_ebtable_check.sh" -tc

log "/nfm/nfm_native_ebtable_check.sh: Deleting Netfilter table entry (name:${netfilter_table_name})"
remove_ovsdb_entry Netfilter -w name "${netfilter_table_name}" &&
    log "/nfm/nfm_native_ebtable_check.sh: Deleting Netfilter table entry (name:${netfilter_table_name}) - Success" ||
    raise "Failed deleting Netfilter table entry (name:${netfilter_table_name})" -l "/nfm/nfm_native_ebtable_check.sh" -tc

log "/nfm/nfm_native_ebtable_check.sh: Checking ebtables rule is removed from the device"
is_ebtables_rule_removed "${table_name}" "${chain_name}" "${ebtable_rule}" "${update_target}" &&
    log "/nfm/nfm_native_ebtable_check.sh: Checking ebtables rule is removed from the device - Success" ||
    raise "Failed, ebtables rule is not removed from the device" -l "/nfm/nfm_native_ebtable_check.sh" -tc

pass
