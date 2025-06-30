#!/bin/sh

#
# Test Adaptive QoS configuration via Interface_QoS/Linux_Queue and AdaptiveQoS on top
#

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

LOG_TAG="$0"

manager_setup_file="qosm/qosm_setup.sh"

usage()
{
cat << usage_string
${0} [-h] arguments
Description:
    - This script configures and validates Adaptive QoS configuration on an OpenSync node by configuring
      IP_Interface/Interface_Qos/Linux_Queue hierarchy, enabling Adaptive QoS and also applying
      AdaptiveQoS custom config on top.
Arguments:
    -h  show this help message
    \$1 <if_name_up>                            : upstream interface for which to configure adaptive QoS         : (string)(required)
    \$2 <if_name_down>                          : downstream interface for which to configure adaptive QoS       : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ${0} <if_name_up> <if_name_down>

Script usage example:
    ${0} dummy_intf_up dummy_intf_down

usage_string
}

reset_config()
{
    remove_ovsdb_entry Wifi_Inet_Config -w if_name "${if_name_up}"
    update_ovsdb_entry IP_Interface -w name "${if_name_up}" -u qos '["set",[]]'
    remove_ovsdb_entry IP_Interface -w name "${if_name_up}"

    remove_ovsdb_entry Wifi_Inet_Config -w if_name "${if_name_down}"
    update_ovsdb_entry IP_Interface -w name "${if_name_down}" -u qos '["set",[]]'
    remove_ovsdb_entry IP_Interface -w name "${if_name_down}"

    empty_ovsdb_table Linux_Queue
    empty_ovsdb_table AdaptiveQoS
    # Interface_QoS is non-root and will be auto-removed when not
    # referenced anymore via any IP_Interface->qos for that interface.
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=2
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s), provided $#" -l "${LOG_TAG}" -arg
if_name_up=$1
if_name_down=$2

check_interface_exists "$if_name_up" &&
    raise "The test case requires that the interface $if_name_up does not exist when the test is ran" -l "${LOG_TAG}" -arg
check_interface_exists "$if_name_down" &&
    raise "The test case requires that the interface $if_name_down does not exist when the test is ran" -l "${LOG_TAG}" -arg

# On any exception during execution, dump debug info and reset config to previous state:
trap '
    fut_ec=$?
    trap - EXIT INT
    echo -e "\n\n"
    fut_info_dump_line
    print_tables IP_Interface Interface_QoS Linux_Queue AdaptiveQoS
    fut_info_dump_line
    reset_config
    exit $fut_ec
' EXIT INT TERM

log_title "${LOG_TAG}: Configuring and validating Adaptive QoS configuration via Interface_QoS/Linux_Queue and AdaptiveQoS"

# Preparation:
reset_config

# Create two dummy interfaces (for UL and for DL) and bring them up:
create_inet_entry \
    -if_name "${if_name_up}" \
    -if_type "tap" \
    -NAT false \
    -ip_assign_scheme "none" \
    -dhcp_sniff "false" \
    -network true \
    -enabled true \
        || raise "Failed to create interface $if_name_up" -l "${LOG_TAG}" -ds

create_inet_entry \
    -if_name "${if_name_down}" \
    -if_type "tap" \
    -NAT false \
    -ip_assign_scheme "none" \
    -dhcp_sniff "false" \
    -network true \
    -enabled true \
        || raise "Failed to create interface $if_name_down" -l "${LOG_TAG}" -ds

# Give the kernel time to actually create the interfaces:
sleep 1

# Configure cake qdisc via Linux_Queue on both interfaces:

cat <<EOF > /tmp/qosm_ovsdb_transact.txt
[
        "Open_vSwitch",
        {
            "op" : "insert",
            "table" : "Linux_Queue",
            "uuid-name": "lnx_queue_up_cake",
            "row" : {
                "parent_id": "root",
                "id": "1:",
                "type": "qdisc",
                "name": "cake",
                "params": "bandwidth 90Mbit diffserv4"
            }
        },
        {
            "op" : "insert",
            "table" : "Linux_Queue",
            "uuid-name": "lnx_queue_down_cake",
            "row" : {
                "parent_id": "root",
                "id": "1:",
                "type": "qdisc",
                "name": "cake",
                "params": "bandwidth 190Mbit diffserv4"
            }
        },
        {
            "op" : "insert",
            "table" : "Interface_QoS",
            "uuid-name": "intf_qos_up",
            "row" : {
                "lnx_queues": ["set", [["named-uuid", "lnx_queue_up_cake"]]]
            }
        },
        {
            "op" : "insert",
            "table" : "Interface_QoS",
            "uuid-name": "intf_qos_down",
            "row" : {
                "lnx_queues": ["set", [["named-uuid", "lnx_queue_down_cake"]]]
            }
        },
        {
            "op" : "insert",
            "table" : "IP_Interface",
            "row" : {
                "name" : "$if_name_up",
                "if_name" : "$if_name_up",
                "enable" : true,
                "qos": ["named-uuid", "intf_qos_up"]
                }
        },
        {
            "op" : "insert",
            "table" : "IP_Interface",
            "row" : {
                "name" : "$if_name_down",
                "if_name" : "$if_name_down",
                "enable" : true,
                "qos": ["named-uuid", "intf_qos_down"]
                }
        }
]
EOF

log "${LOG_TAG}: Configuring cake for UL and DL: Transacting IP_Interface/Interface_QoS/Linux_Queue ..."

ovsdb-client transact "$(cat /tmp/qosm_ovsdb_transact.txt)" 2>&1 | grep -i 'error' &&
    raise "ovsdb-client transact error configuring QoS" -l "${LOG_TAG}" -fc

uuid_up=$(get_ovsdb_entry_value IP_Interface qos -w "name" "$if_name_up") ||
    raise "failed getting IP_Interface->qos for UL interface" -l "${LOG_TAG}" -fc

uuid_down=$(get_ovsdb_entry_value IP_Interface qos -w "name" "$if_name_down") ||
    raise "failed getting IP_Interface->qos for DL interface" -l "${LOG_TAG}" -fc

# Verify success:
wait_ovsdb_entry Interface_QoS \
    -w _uuid "[\"uuid\",\"$uuid_up\"]" \
    -is status "success" -t 5 &&
        log "${LOG_TAG}: Linux cake qdisc QoS configured for UL - Success" ||
        raise "Failed configuring Linux cake qdisc QoS for UL" -l "${LOG_TAG}" -fc

wait_ovsdb_entry Interface_QoS \
    -w _uuid "[\"uuid\",\"$uuid_down\"]" \
    -is status "success" -t 5 &&
        log "${LOG_TAG}: Linux cake qdisc QoS configured for DL - Success" ||
        raise "Failed configuring Linux cake qdisc QoS for DL" -l "${LOG_TAG}" -fc

# Configure Adaptive QoS on top, for both upstream and downstream:

cat <<EOF > /tmp/qosm_ovsdb_transact.txt
[
        "Open_vSwitch",
        {
            "op" : "update",
            "table" : "Interface_QoS",
            "where" : [[ "_uuid", "==", ["uuid","$uuid_up"] ]],
            "row" : {
                "adaptive_qos": ["map", [["min_rate","40000"],["base_rate","170000"],["max_rate","190000"],["direction","UL"]]]
            }
        },
        {
            "op" : "update",
            "table" : "Interface_QoS",
            "where" : [[ "_uuid", "==", ["uuid","$uuid_down"] ]],
            "row" : {
                "adaptive_qos": ["map", [["min_rate","20000"],["base_rate","70000"],["max_rate","90000"],["direction","DL"]]]
            }
        }
]
EOF

log "${LOG_TAG}: Configuring Adaptive QoS for UL and DL: Setting adaptive_qos to relevant Interface_QoS ..."

ovsdb-client transact "$(cat /tmp/qosm_ovsdb_transact.txt)" 2>&1 | grep -i 'error' &&
    raise "ovsdb-client transact error configuring Adaptive QoS" -l "${LOG_TAG}" -fc

sleep 4

# Check if cake-autorate is running:
cake_autorate_pids=$(get_pid "cake-autorate")
log -deb "${LOG_TAG}: Got cake_autorate_pids: $cake_autorate_pids"
[ -n "$cake_autorate_pids" ] &&
    log "cake-autorate running -- Success" ||
    raise "cake-autorate NOT running" -l "${LOG_TAG}" -tc

echo -e "\n"
log_title "${LOG_TAG}: Success"
echo -e "\n"

# Now, test AdaptiveQoS custom config on top:
insert_ovsdb_entry AdaptiveQoS \
    -i reflectors_list "1.1.1.1 8.8.8.8 9.9.9.10 9.9.9.11" \
    -i num_pingers 2 \
    -i ping_interval 337 \
    -i active_thresh_kbps 3000 ||
    raise "Failed inserting AdaptiveQoS custom config" -l "${LOG_TAG}" -tc

sleep 4

# Check if cake-autorate is (still) running and if custom parameters applied (check actual fping interval):
cake_autorate_pids=$(get_pid "cake-autorate")
log -deb "${LOG_TAG}: Got cake_autorate_pids: $cake_autorate_pids"
[ -n "$cake_autorate_pids" ] &&
    log "cake-autorate running -- Success" ||
    raise "cake-autorate NOT running" -l "${LOG_TAG}" -tc

# Check if fping running with modified parameters:
fping_modified_params=$(ps | grep fping | grep 'period 337')
[ -n "$fping_modified_params" ] &&
    log "AdaptiveQoS custom parameters modification -- Success" ||
    raise "AdaptiveQoS custom parameters failed to apply" -l "${LOG_TAG}" -tc

# Now, unset adaptive_qos for one of the interfaces, and verify that Adaptive QoS is then
# deconfigured (cake-autorate no longer running):

# update_ovsdb_entry() does not digest well the syntax _uuid==["uuid","<uuid>"] where
# double quotes need to be preserved (shell expansion problem), thus doing it manually.
log -deb "${LOG_TAG}: Unsetting adaptive_qos for the upstream interface and testing if Adaptive QoS will get disabled\n\t"
/usr/opensync/tools/ovsh --quiet --timeout=180000 u Interface_QoS  \
    -w _uuid==[\"uuid\",\""$uuid_up"\"] \
    adaptive_qos:='["map",[]]' 2>&1 ||
        raise "Failed unsetting Interface_QoS->adaptive_qos for UL interface" -l "${LOG_TAG}" -fc

sleep 4

cake_autorate_pids=$(get_pid "cake-autorate")
log --deb "${LOG_TAG}: Got cake_autorate_pids: $cake_autorate_pids"
[ -z "$cake_autorate_pids" ] &&
    log "cake-autorate no longer running -- Success" ||
    raise "cake-autorate STILL running" -l "${LOG_TAG}" -tc

# Cleanup:
reset_config
trap - EXIT INT TERM

pass
