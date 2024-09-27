#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
# shellcheck disable=SC3046
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="nm2/nm2_setup.sh"

usage()
{
cat << usage_string
nm2/nm2_verify_linux_traffic_control_rules_template_rules.sh [-h] arguments
Description:
    - Script configures Interface_Classifier and IP_Interface tables, through which the linux Traffic Control template rules
    are applied on the device.  Also verifies if the linux Traffic Control configuration is applied on the system.
    - Modify and delete operations is also validated.
Arguments:
    -h  show this help message
    \$1 (if_name)           : Interface name                                         : (string)(required)
    \$2 (ig_match)          : Ingress match string                                   : (string)(required)
    \$3 (ig_action)         : Ingress action string                                  : (string)(required)
    \$4 (ig_tag_name)       : Tag name used in Ingress match string                  : (string)(required)
    \$5 (eg_match)          : Egress match string                                    : (string)(required)
    \$6 (eg_action)         : Egress action string                                   : (string)(required)
    \$7 (eg_match_with_tag) : Egress match string with tag value                     : (string)(required)
    \$8 (eg_expected_str)   : Expected output for checking if egress rule is applied : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./nm2/nm2_verify_linux_traffic_control_rules_template_rules.sh <IF_NAME> <IG_MATCH> <IG_ACTION> <IG_TAG_NAME>
                      <EG_MATCH> <EG_ACTION> <EG_MATCH_WITH_TAG> <EG_EXPECTED_STR>
Script usage example:
    ./nm2/nm2_verify_linux_traffic_control_rules_template_rules.sh dummy-intf "ip flower dst_mac \${devices_tag}" \
                "action mirred egress mirror dev br-home" "devices_tag" \
                "ip flower ip_proto udp src_port 67" "action mirred egress redirect dev br-home" \
                "ip flower dst_mac \${devices_tag}" "67"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=8
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -arg
if_name=$1
ingress_match_with_tag=$2
ingress_action=$3
tag_name=$4
egress_match=$5
egress_action=$6
egress_match_with_tag=$7
egress_expected_str=$8

ic_egress_token="dev_eg_${if_name}"
ic_egress_token_with_tag="dev_eg_${if_name}_tag"
ic_ingress_token="dev_ig_${if_name}"
ip_intf_name="dev_ip_intf"

# port address used for template tag
port1="80"
port2="8080"

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Openflow_Tag IP_Interface Interface_Classifier
    reset_inet_entry $if_name || true
    run_setup_if_crashed nbm || true
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "nm2/nm2_verify_linux_traffic_control_rules.sh:  Configuring and Validating Linux Traffic Control template Rule"

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Creating Wifi_Inet_Config entries for $if_name (if_type:tap)"
create_inet_entry \
    -if_name "${if_name}" \
    -if_type "tap" \
    -NAT false \
    -ip_assign_scheme "none" \
    -dhcp_sniff "false" \
    -network true \
    -enabled true &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Interface $if_name created - Success" ||
        raise "Failed to create interface $if_name" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

# create Interface classifier for ingress
log "nm2/nm2_verify_linux_traffic_control_rules.sh: - Creating Interface_Classifier '$ic_ingress_token' (match:'$ingress_match_with_tag')"
insert_ovsdb_entry Interface_Classifier \
    -i token "$ic_ingress_token" \
    -i priority 2 \
    -i match "$ingress_match_with_tag" \
    -i action "$ingress_action" &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Interface classifier $ic_ingress_token created - Success" ||
        raise "Failed to create interface classifier $ic_ingress_token" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

# create Interface classifier with template match for egress
log "nm2/nm2_verify_linux_traffic_control_rules.sh: - Creating Interface_Classifier '$ic_ingress_token' (match:'$egress_match_with_tag')"
insert_ovsdb_entry Interface_Classifier \
    -i token "$ic_egress_token_with_tag" \
    -i priority 2 \
    -i match "$egress_match_with_tag" \
    -i action "$ingress_action" &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Interface classifier $ic_egress_token_with_tag created - Success" ||
        raise "Failed to create interface classifier $ic_egress_token_with_tag" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

# create Interface classifier for egress
log "nm2/nm2_verify_linux_traffic_control_rules.sh: - Creating Interface_Classifier '$ic_egress_token' (match:'$egress_match')"
insert_ovsdb_entry Interface_Classifier \
    -i token "$ic_egress_token" \
    -i priority 2 \
    -i match "$egress_match" \
    -i action "$egress_action" &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Interface classifier $ic_ingress_token created - Success" ||
        raise "Failed to create interface classifier $ic_ingress_token" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Getting uuid for Interface classifier '$ic_ingress_token'"
ic_ingress_uuid=$(get_ovsdb_entry_value Interface_Classifier _uuid -w "token" "$ic_ingress_token") ||
    raise "Failed to get uuid for Interface Classifier" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Getting uuid for Interface classifier '$ic_egress_token'"
ic_egress_uuid=$(get_ovsdb_entry_value Interface_Classifier _uuid -w "token" "$ic_egress_token") ||
    raise "Failed to get uuid for Interface Classifier" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Getting uuid for Interface classifier '$ic_egress_token_with_tag'"
ic_egress_with_tag_uuid=$(get_ovsdb_entry_value Interface_Classifier _uuid -w "token" "$ic_egress_token_with_tag") ||
    raise "Failed to get uuid for Interface Classifier" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

# create IP_Interface and set the ingress rule
log "nm2/nm2_verify_linux_traffic_control_rules.sh: Creating IP_Interface '$ip_intf_name' with ingress rule"
insert_ovsdb_entry IP_Interface \
    -i if_name "${if_name}" \
    -i name "$ip_intf_name" \
    -i ingress_classifier '["set",[["uuid","'${ic_ingress_uuid}'"]]]' &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: IP_Interface $ip_intf_name created - Success" ||
        raise "Failed to create IP_Interface $ip_intf_name" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

# creating openflow_Tag after the tag is referenced.  The rule should be
# updated with the tag value.
insert_ovsdb_entry Openflow_Tag \
    -i name "${tag_name}" \
    -i cloud_value '["set",["'${port1}'","'${port2}'"]]' &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Entry inserted to Openflow_Tag for name '$tag_name'  - Success" ||
        raise "Failed to insert $tag_name in Openflow_Tag table" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -fc

# verify if the ingress configuration with tag value is applied correctly in the system
port1_hexval=$(printf '%x\n' $port1)
log "nm2/nm2_verify_linux_traffic_control_rules.sh:  port1_hexval '$port1_hexval' "
nb_is_tc_rule_configured "${if_name}" ${port1_hexval} "ingress" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: Ingress Traffic Control rule with ${port1} is configured on device - Success" ||
    raise "failed Traffic Control rule with ${port1} is configured on device" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

port2_hexval=$(printf '%x\n' $port2)
log "nm2/nm2_verify_linux_traffic_control_rules.sh:  port2_hexval '$port2_hexval' "
nb_is_tc_rule_configured "${if_name}" ${port2_hexval} "ingress" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: Ingress Traffic Control rule with ${port2} is configured on device - Success" ||
    raise "failed Traffic Control rule with ${port2} is configured on device" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Updating IP_Interface '$ip_intf_name' with egress rule "
update_ovsdb_entry IP_Interface \
    -w if_name "${if_name}" \
    -u egress_classifier '["set",[["uuid","'${ic_egress_uuid}'"]]]' &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Updating IP_Interface $ip_intf_name with egress rule - Success" ||
        raise "Updating IP_Interface $ip_intf_name with egress rule" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

# verify if the egress classifier rule is applied in the system (L2 check)
nb_is_tc_rule_configured ${if_name} ${egress_expected_str} "egress" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: Egress Traffic Control rule with ${egress_expected_str} is configured on device - Success" ||
    raise "failed Egress Traffic Control rule with ${egress_expected_str} is configured on device" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Updating IP_Interface '$ip_intf_name' with egress tag rule "
update_ovsdb_entry IP_Interface \
    -w if_name "${if_name}" \
    -u egress_classifier '["set",[["uuid","'${ic_egress_with_tag_uuid}'"]]]' &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Updating IP_Interface $ip_intf_name with egress rule - Success" ||
        raise "Updating IP_Interface $ip_intf_name with egress rule" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

# verify if the egress configuration is applied correctly in the system
nb_is_tc_rule_configured ${if_name} ${port1_hexval} "egress" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: Egress Traffic Control rule with ${port1} is configured on device - Success" ||
    raise "Failed Egress Traffic Control rule with ${port1} is configured on device" -l "nm2/nm2_verify_linux_traffic_control_rules.sh:" -fc

# Delete Interface Classifiers and IP_Interface
log "nm2/nm2_verify_linux_traffic_control_rules.sh: Removing ingress and egress classifiers from '$ip_intf_name'"
update_ovsdb_entry IP_Interface \
    -w if_name "${if_name}" \
    -u egress_classifier '["set", ['']]' \
    -u ingress_classifier '["set", ['']]' &&
        log "nm2/nm2_verify_linux_traffic_control_rules.sh: Removing ingress and egress classifiers from '$ip_intf_name' - Success" ||
        raise "Removing ingress and egress classifiers from '$ip_intf_name'" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -ds

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Clean up ingress Interface Classifier ${ic_ingress_token}"
remove_ovsdb_entry Interface_Classifier -w token "${ic_ingress_token}" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: OVSDB entry from Interface_Classifier removed for $ic_ingress_token - Success" ||
    log -err "nm2/nm2_verify_linux_traffic_control_rules.sh: Failed to remove OVSDB entry from Interface_Classifier for $ic_ingress_token"

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Clean up ingress Interface Classifier ${ic_egress_token}"
remove_ovsdb_entry Interface_Classifier -w token "${ic_egress_token}" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: OVSDB entry from Interface_Classifier removed for $ic_egress_token - Success" ||
    log -err "nm2/nm2_verify_linux_traffic_control_rules.sh: Failed to remove OVSDB entry from Interface_Classifier for $ic_egress_token"

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Clean up ingress Interface Classifier ${ic_egress_token_with_tag}"
remove_ovsdb_entry Interface_Classifier -w token "${ic_egress_token_with_tag}" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: OVSDB entry from Interface_Classifier removed for $ic_egress_token_with_tag - Success" ||
    log -err "nm2/nm2_verify_linux_traffic_control_rules.sh: Failed to remove OVSDB entry from Interface_Classifier for $ic_egress_token_with_tag"

log "nm2/nm2_verify_linux_traffic_control_rules.sh: Clean up IP_Interface ${ip_intf_name}"
remove_ovsdb_entry IP_Interface -w name "${ip_intf_name}" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: OVSDB entry from IP_Interface removed for $ip_intf_name - Success" ||
    log -err "nm2/nm2_verify_linux_traffic_control_rules.sh: Failed to remove OVSDB entry from IP_Interface for $ip_intf_name"

log "nm2/nm2_verify_linux_traffic_control_rules.sh: clean up interface $if_name"
delete_inet_interface "$if_name" &&
    log "nm2/nm2_verify_linux_traffic_control_rules.sh: interface $if_name removed from device - Success" ||
    raise "interface $if_name not removed from device" -l "nm2/nm2_verify_linux_traffic_control_rules.sh" -tc

pass
