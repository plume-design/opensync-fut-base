#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
fsm/fsm_create_tap_interface.sh [-h] arguments
Description:
    - Script creates and configures tap interface as a part of fsm plugin configuration.

Arguments:
    -h  show this help message
    \$1 (lan_bridge_if_name)  : used as bridge interface name          : (string)(required)
    \$2 (postfix)             : used as postfix on tap interface name  : (string)(required)
    \$3 (of_port)             : used as Openflow port                  : (int)(required)

Script usage example:
    ./fsm/fsm_create_tap_interface.sh br-home tdns 3001
    ./fsm/fsm_create_tap_interface.sh br-home thttp 4001
    ./fsm/fsm_create_tap_interface.sh br-home tupnp 5001
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
fut_info_dump_line
show_bridge_details
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -arg
lan_bridge_if_name=${1}
tap_name_postfix=${2}
of_port=${3}

# Construct from input arguments
tap_if="${lan_bridge_if_name}.${tap_name_postfix}"

log_title "fsm/fsm_create_tap_interface.sh: FSM test - Create tap interface - $tap_if"

# Generate tap interface
log "fsm/fsm_create_tap_interface.sh: Generate tap interface '$tap_if'"
wait_for_function_response 0 "add_tap_interface $lan_bridge_if_name $tap_if $of_port" &&
    log "fsm/fsm_create_tap_interface.sh: add_tap_interface - interface '$tap_if' created on '$lan_bridge_if_name'- Success" ||
    raise "FAIL: add_tap_interface - interface '$tap_if' not created" -l "fsm/fsm_create_tap_interface.sh" -tc

# Bring up tap interface DNS
wait_for_function_response 0 "tap_up_cmd $tap_if" &&
    log "fsm/fsm_create_tap_interface.sh: tap_up_cmd - interface '$tap_if' brought up - Success" ||
    raise "FAIL: tap_up_cmd - interface '$tap_if' not brought up" -l "fsm/fsm_create_tap_interface.sh" -tc

# Set no flood to interface DNS
wait_for_function_response 0 "gen_no_flood_cmd $lan_bridge_if_name $tap_if" &&
    log "fsm/fsm_create_tap_interface.sh: gen_no_flood_cmd - set interface '$tap_if' to 'no flood' - Success" ||
    raise "FAIL: gen_no_flood_cmd - interface '$tap_if' not set to 'no flood'" -l "fsm/fsm_create_tap_interface.sh" -tc

# Check if applied to system (LEVEL2)
wait_for_function_response 0 "check_if_port_in_bridge $tap_if $lan_bridge_if_name" &&
    log "fsm/fsm_create_tap_interface.sh: check_if_port_in_bridge - LEVEL2 - port '$tap_if' added to '$lan_bridge_if_name' - Success" ||
    raise "FAIL: check_if_port_in_bridge - LEVEL2 - port '$tap_if' not added to $lan_bridge_if_name" -l "fsm/fsm_create_tap_interface.sh" -tc

# Show ovs switch config
show_bridge_details

# Delete port from bridge
wait_for_function_response 0 "remove_port_from_bridge $lan_bridge_if_name $tap_if" &&
    log "fsm/fsm_create_tap_interface.sh: remove_port_from_bridge - port '$tap_if' removed from '$lan_bridge_if_name' - Success" ||
    raise "FAIL: remove_port_from_bridge - port '$tap_if' not removed from '$lan_bridge_if_name'" -l "fsm/fsm_create_tap_interface.sh" -tc

pass
