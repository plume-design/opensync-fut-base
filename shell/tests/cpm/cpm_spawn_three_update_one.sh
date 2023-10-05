#!/bin/sh

# Spawn three tinyproxy processes, then update one

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
cpm/cpm_spawn_three_update_one.sh [-h] arguments
Description:
    - Spawn three tinyproxy processes, then update one
Arguments:
    -h : show this help message
Script usage example:
    ./cpm/cpm_spawn_three_update_one.sh
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

init_cpm_test()
{
    empty_ovsdb_table Captive_Portal
    killall tinyproxy
    pidof cpm || ovsh u Node_Services enable:=true -w service==cpm
}

validate_tinyproxies()
{
    tinyproxy_pids=$(pidof tinyproxy)
    for pid in $tinyproxy_pids
    do
        uuid=$(cat /proc/"$pid"/cmdline | grep -Eo "tinyproxy\..*\.conf" | sed 's/tinyproxy\.//' | sed 's/\.conf//')
        if [ -z "$uuid" ]; then
            log "No tinyproxies found with the following uuid: $uuid"
            return 1
        fi
        command=\"ovsh s Captive_Portal -c -w _uuid=='["uuid", '"$uuid"']'\"
        eval "$command"
    done
}


trap '
fut_info_dump_line
print_tables Captive_Portal
ps -w | grep tinyproxy | grep -v grep
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "cpm/cpm_spawn_three_update_one.sh: CPM test - Verify CPM spawning tinyproxies"

init_cpm_test

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "default" \
-i other_config '["map",[["pkt_mark","0x2"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal1" &&
    log "cpm/cpm_spawn_three_update_one.sh: First Captive_Portal entry inserted - Success" ||
    raise "FAIL: Failed to insert first Captive_Portal entry" -l "cpm/cpm_spawn_three_update_one.sh" -oe

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "employee" \
-i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8889"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal2" &&
    log "cpm/cpm_spawn_three_update_one.sh: Second Captive_Portal entry inserted - Success" ||
    raise "FAIL: Failed to insert second Captive_Portal entry" -l "cpm/cpm_spawn_three_update_one.sh" -oe

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "group" \
-i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8890"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal3" &&
    log "cpm/cpm_spawn_three_update_one.sh: Third Captive_Portal entry inserted - Success" ||
    raise "FAIL: Failed to insert third Captive_Portal entry" -l "cpm/cpm_spawn_three_update_one.sh" -oe

update_ovsdb_entry Captive_Portal \
-w name "employee" \
-u other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8891"]]]' \
-u uam_url "https://captiveportal4" &&
    log "cpm/cpm_spawn_three_update_one.sh: Third Captive_Portal entry updated - Success" ||
    raise "FAIL: Failed to update third Captive_Portal entry" -l "cpm/cpm_spawn_three_update_one.sh" -oe

# debounce timer 1 sec plus 1 sec add-on for tinyproxies to get created
sleep 2

validate_tinyproxies &&
    log "cpm/cpm_spawn_three_update_one.sh: Captive_Portal entries handled - Success" ||
    raise "FAIL: Captive_Portal entries handling failed"  -l "cpm/cpm_spawn_three_update_one.sh" -tc

print_tables Captive_Portal

pass
