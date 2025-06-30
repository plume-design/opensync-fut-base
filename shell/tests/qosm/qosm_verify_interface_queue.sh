#!/bin/sh

#
# Test basic QoS configuration on an interface via Interface_QoS/Interface_Queue
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
    - This script configures and validates basic QoS (rate limiting) on an OpenSync node by configuring
      IP_Interface/Interface_Qos/Interface_Queue.
Arguments:
    -h  show this help message
    \$1 <if_name>                            : interface for which to configure QoS         : (string)(required)

Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ${0} <if_name>

Script usage example:
    ${0} dummy_intf

usage_string
}

reset_config()
{
    remove_ovsdb_entry Wifi_Inet_Config -w if_name "${if_name}"
    update_ovsdb_entry IP_Interface -w name "${if_name}" -u qos '["set",[]]'
    remove_ovsdb_entry IP_Interface -w name "${if_name}"
    # Interface_QoS and Interface_Queue are non-root and will be auto-removed when not
    # referenced anymore via any IP_Interface->qos for that interface.
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=1
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s), provided $#" -l "${LOG_TAG}" -arg
if_name=$1

check_interface_exists "$if_name" &&
    raise "The test case requires that the interface $if_name does not exist when the test is ran" -l "${LOG_TAG}" -arg

# On any exception during execution, dump debug info and reset config to previous state:
trap '
    fut_ec=$?
    trap - EXIT INT
    echo -e "\n\n"
    fut_info_dump_line
    print_tables IP_Interface Interface_QoS Interface_Queue
    fut_info_dump_line
    reset_config
    exit $fut_ec
' EXIT INT TERM

log_title "${LOG_TAG}: Configuring and validating QoS configuration via Interface_QoS/Interface_Queue"

# Preparation:
reset_config

# Create a dummy interface and bring it up:
create_inet_entry \
    -if_name "${if_name}" \
    -if_type "tap" \
    -NAT false \
    -ip_assign_scheme "none" \
    -dhcp_sniff "false" \
    -network true \
    -enabled true \
        || raise "Failed to create interface $if_name" -l "${LOG_TAG}" -ds

# Give the kernel time to actually create the interface:
sleep 1

# Configure QoS on the interface:
cat <<EOF > /tmp/qosm_ovsdb_transact.txt
[
        "Open_vSwitch",
        {
            "op" : "insert",
            "table" : "Interface_Queue",
            "uuid-name": "named_uuid_interface_queue",
            "row" : {
                "bandwidth": 21337,
                "priority": 1,
                "tag": "fut_test_qos"
            }
        },
        {
            "op" : "insert",
            "table" : "Interface_QoS",
            "uuid-name": "named_uuid_interface_qos",
            "row" : {
                "queues": ["set", [["named-uuid", "named_uuid_interface_queue"]]]
            }
        },
        {
            "op" : "insert",
            "table" : "IP_Interface",
            "row" : {
                "name" : "$if_name",
                "if_name" : "$if_name",
                "enable" : true,
                "qos": ["named-uuid", "named_uuid_interface_qos"]
                }
        }
]
EOF

log "${LOG_TAG}: Transacting IP_Interface/Interface_QoS/Interface_Queue ..."

ovsdb-client transact "$(cat /tmp/qosm_ovsdb_transact.txt)" 2>&1 | grep -i 'error' &&
    raise "ovsdb-client transact error configuring QoS" -l "${LOG_TAG}" -fc

uuid=$(get_ovsdb_entry_value IP_Interface qos -w "name" "$if_name") ||
    raise "failed getting IP_Interface->qos" -l "${LOG_TAG}" -fc

# Verify success:
wait_ovsdb_entry Interface_QoS \
    -w _uuid "[\"uuid\",\"$uuid\"]" \
    -is status "success" -t 5 &&
        log "${LOG_TAG}: QoS configured - Success" ||
        raise "Failed configuring rate limit QoS" -l "${LOG_TAG}" -fc

# Check if modification works:
update_ovsdb_entry Interface_Queue -w bandwidth 21337 -u bandwidth 1337

# Just in case sleep so we don't actually check for previous status which might not have been updated:
sleep 1

wait_ovsdb_entry Interface_QoS \
    -w _uuid "[\"uuid\",\"$uuid\"]" \
    -is status "success" -t 5 &&
        log "${LOG_TAG}: QoS configured - Success" ||
        raise "Failed modifying  rate limit QoS" -l "${LOG_TAG}" -fc

echo -e "\n"
log_title "${LOG_TAG}: Success      "
echo -e "\n"

# Cleanup:
reset_config
trap - EXIT INT TERM

pass
