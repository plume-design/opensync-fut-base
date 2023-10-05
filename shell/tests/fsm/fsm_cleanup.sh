#!/bin/sh

# Clean up after tests for FSM.

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

fsm_vif_name=${1}
shift
lan_bridge_if_name=${1}
shift

log "fsm/fsm_cleanup.sh: Cleaning FSM OVSDB Config tables"
empty_ovsdb_table Openflow_Config
empty_ovsdb_table Flow_Service_Manager_Config
empty_ovsdb_table FSM_Policy
empty_ovsdb_table Openflow_Tag

if [ "${fsm_vif_name}" != false ]; then
    log "fsm/fsm_cleanup.sh: Removing $fsm_vif_name from $lan_bridge_if_name"
    remove_port_from_bridge "$lan_bridge_if_name" "$fsm_vif_name" &&
        log "fsm/fsm_cleanup.sh: remove_port_from_bridge - Removed $fsm_vif_name from $lan_bridge_if_name - Success" ||
        log -err "fsm/fsm_cleanup.sh: Failed to remove $fsm_vif_name from $lan_bridge_if_name"
    log "fsm/fsm_cleanup.sh: Removing Wifi_VIF_Config '${fsm_vif_name}' entry"
    remove_ovsdb_entry Wifi_VIF_Config -w if_name "${fsm_vif_name}" &&
        log "fsm/fsm_cleanup.sh: Wifi_VIF_Config::if_name = ${fsm_vif_name} entry removed - Success" ||
        log -err "fsm/fsm_cleanup.sh: Failed to remove Wifi_VIF_Config::if_name = ${fsm_vif_name} entry"
    wait_ovsdb_entry_remove Wifi_VIF_State -w if_name "${fsm_vif_name}"  &&
        log "fsm/fsm_cleanup.sh: Wifi_VIF_State::if_name = ${fsm_vif_name} entry removed - Success" ||
        log -err "fsm/fsm_cleanup.sh: Failed to remove Wifi_VIF_State::if_name = ${fsm_vif_name} entry"

    log "fsm/fsm_cleanup.sh: Removing Wifi_Inet_Config '${fsm_vif_name}' entry"
    remove_ovsdb_entry Wifi_Inet_Config -w if_name "${fsm_vif_name}" &&
        log "fsm/fsm_cleanup.sh: Wifi_Inet_Config::if_name = ${fsm_vif_name} entry removed - Success" ||
        log -err "fsm/fsm_cleanup.sh: Failed to remove Wifi_Inet_Config::if_name = ${fsm_vif_name} entry"
    wait_ovsdb_entry_remove Wifi_Inet_State -w if_name "${fsm_vif_name}"  &&
        log "fsm/fsm_cleanup.sh: Wifi_Inet_State::if_name = ${fsm_vif_name} entry removed - Success" ||
        log -err "fsm/fsm_cleanup.sh: Failed to remove Wifi_Inet_State::if_name = ${fsm_vif_name} entry"
fi

for fsm_inet_if_name in "$@"
    do
        log "fsm/fsm_cleanup.sh: Removing Wifi_Inet_Config '${fsm_inet_if_name}' entry"
        remove_ovsdb_entry Wifi_Inet_Config -w if_name "${fsm_inet_if_name}" &&
            log "fsm/fsm_cleanup.sh: Wifi_Inet_Config::if_name = ${fsm_inet_if_name} entry removed - Success" ||
            log -err "fsm/fsm_cleanup.sh: Failed to remove Wifi_Inet_Config::if_name = ${fsm_inet_if_name} entry"
        wait_ovsdb_entry_remove Wifi_Inet_State -w if_name "${fsm_inet_if_name}" &&
            log "fsm/fsm_cleanup.sh: Wifi_Inet_State::if_name = ${fsm_inet_if_name} entry removed - Success" ||
            log -err "fsm/fsm_cleanup.sh: Failed to remove Wifi_Inet_State::if_name = ${fsm_inet_if_name} entry"
        log "fsm/fsm_cleanup.sh: Removing $fsm_inet_if_name from $lan_bridge_if_name"
        remove_port_from_bridge "$lan_bridge_if_name" "$fsm_inet_if_name" &&
            log "fsm/fsm_cleanup.sh: remove_port_from_bridge - Removed $fsm_inet_if_name from $lan_bridge_if_name - Success" ||
            log -err "fsm/fsm_cleanup.sh: Failed to remove $fsm_inet_if_name from $lan_bridge_if_name"
    done

print_tables Wifi_Inet_Config
print_tables Wifi_Inet_State
print_tables Wifi_VIF_Config
print_tables Wifi_VIF_State

show_bridge_details
