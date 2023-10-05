#!/bin/sh

# Test deleting an instance while its tinyproxy is restarting
#
# Restarting tinyproxy takes place for about 10 seconds after insert,
# given that another tinyproxy is already running on the same listenip
# and listenport.
# Here the second instance is deleted about 5 seconds after insert
# At the end it is checked that everything is just as if the second
# instance never existed.
#



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
cpm/cpm_delete_while_restarting.sh [-h] arguments
Description:
    - Script validates deleting an instance while its tinyproxy is restarting
    - Script checks that crashed tinyproxies are replaced by new ones
Arguments:
    -h : show this help message
Script usage example:
    ./cpm/cpm_delete_while_restarting.sh
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

validate_delete()
{
    retval=1
    uuid_1=$(get_ovsdb_entry_value Captive_Portal _uuid -w name "default")
    tp_count=$(pidof tinyproxy | wc -w)
    if [ "$tp_count" = "1" ]; then
        tp_pid=$(ps -w | grep tinyproxy | grep -v grep | awk '{print $1}')
        tp_uuid_1=$(cat /proc/"$tp_pid"/cmdline | grep -Eo "$uuid_1")
        if [ "$tp_uuid_1" = "$uuid_1" ]; then
            tp_config_count=$(ls -l /tmp/tinyproxy | wc -l)
            if [ "$tp_config_count" = "1" ]; then
                retval=0
            fi
        fi
    fi
    return $retval
}

trap '
fut_info_dump_line
print_tables Captive_Portal
echo "Final tinyproxies status:"
ps -w | grep tinyproxy | grep -v grep
echo "Final tinyproxies config files status:"
ls -l /tmp/tinyproxy
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "cpm/cpm_delete_while_restarting.sh: CPM test - Verify deleting a tinproxy instance while tinyproxy is restarting"

init_cpm_test

# make sure there are no zombie config files
rm -f /tmp/tinyproxy/tinyproxy.*.conf
    log "cpm/cpm_same_ip_port.sh: Removed tinyproxy configuration file - Success" ||
    raise "FAIL: Unable to remove tinyproxy configuration file" -l "cpm/cpm_same_ip_port.sh" -tc

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "default" \
-i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8889"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal1" &&
    log "cpm/cpm_delete_while_restarting.sh: First Captive_Portal entry inserted - Success" ||
    raise "FAIL: Failed to insert first Captive_Portal entry" -l "cpm/cpm_delete_while_restarting.sh" -oe

# debounce timer 1 second plus one additional second
sleep 2

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "group" \
-i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8888"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal2" &&
    log "cpm/cpm_delete_while_restarting.sh: Second Captive_Portal entry inserted - Success" ||
    raise "FAIL: Failed to insert second Captive_Portal entry" -l "cpm/cpm_delete_while_restarting.sh" -oee

log "tinyproxy status before deleting an entry:"
ps -w | grep tinyproxy | grep -v grep
ls -l /tmp/tinyproxy

# deleting
sleep 5

remove_ovsdb_entry Captive_Portal -w name "group" &&
    log "cpm/cpm_delete_while_restarting.sh: Successfully removed Captive_Portal entry - Success" ||
    raise "FAIL: IUnable to remove Captive_Portal entry"  -l "cpm/cpm_delete_while_restarting.sh" -tc

log "tinyproxy status after deleting an entry:"
ps -w | grep tinyproxy | grep -v grep
ls -l /tmp/tinyproxy

validate_delete &&
    log "cpm/cpm_delete_while_restarting.sh: Only the first tinyproxy found - Success" ||
    raise "FAIL: Incorrect validation result"  -l "cpm/cpm_delete_while_restarting.sh" -tc

print_tables Captive_Portal

pass
