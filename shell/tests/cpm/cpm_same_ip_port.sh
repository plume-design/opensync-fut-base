#!/bin/sh

# Test two tinyproxies listening on the same ip and port
#
# The first one should be set up normally while the second should exit
# immediately with 'Could not create listening sockets'.
# According to the daemon_restart_set input in cportal_proxy_init,
# restart is tried 10 times before giving up.
# So the end state should be two Captive_Portal entries with the
# same listenip and listenport and only one tinyproxy process running.
# Also the config file /tmp/tinyproxy/tinyproxy.<uuid>.conf of the
# abandoned process stays undeleted for ever.
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
cpm/cpm_same_ip_port.sh [-h] arguments
Description:
    - Check that crashed tinyproxies are replaced by new ones
Arguments:
    -h : show this help message
Script usage example:
    ./cpm/cpm_same_ip_port.sh
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

validate_1_up_2_gone()
{
    retval=1
    uuid_1=$(get_ovsdb_entry_value Captive_Portal _uuid -w name "default")
    tp_count=$(pidof tinyproxy | wc -w)
    if [ "$tp_count" = "1" ]; then
        tp_pid=$($(get_process_cmd) | grep tinyproxy | grep -v grep | awk '{print $1}')
        tp_uuid_1=$(cat /proc/"$tp_pid"/cmdline | grep -Eo "$uuid_1")
        if [ "$tp_uuid_1" = "$uuid_1" ]; then
            tp_config_count=$(ls -l /tmp/tinyproxy | wc -l)
            if [ "$tp_config_count" = "2" ]; then
                # success - two config files: one of the running and one
                # of the abandoned tinyproxy after 10 restart retries.
                retval=0
            fi
        fi
    fi
    return $retval
}

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Captive_Portal
    echo "Final tinyproxies status:"
    $(get_process_cmd) | grep tinyproxy | grep -v grep
    echo "Final tinyproxies config files status:"
    ls -l /tmp/tinyproxy
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

log_title "cpm/cpm_same_ip_port.sh: CPM test - Verify default listen ip and port"

init_cpm_test

# make sure there are no zombie config files
rm -f /tmp/tinyproxy/tinyproxy.*.conf
    log "cpm/cpm_same_ip_port.sh: Removed tinyproxy configuration file - Success" ||
    raise "Unable to remove tinyproxy configuration file" -l "cpm/cpm_same_ip_port.sh" -tc

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "default" \
-i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8889"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal1" &&
    log "cpm/cpm_same_ip_port.sh: First Captive_Portal entry inserted - Success" ||
    raise "Failed to insert first Captive_Portal entry" -l "cpm/cpm_same_ip_port.sh" -tc

# debounce timer 1 second plus one additional second
sleep 2

insert_ovsdb_entry Captive_Portal \
-i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
-i name "group" \
-i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8889"]]]' \
-i proxy_method "reverse" \
-i uam_url "https://captiveportal2" &&
    log "cpm/cpm_same_ip_port.sh: Second Captive_Portal entry inserted - Success" ||
    raise "Failed to insert second Captive_Portal entry" -l "cpm/cpm_same_ip_port.sh" -tc

# for restarting 10 times debounce timer plus some add-on
sleep 15

validate_1_up_2_gone &&
    log "cpm/cpm_same_ip_port.sh: Found the first tinyproxy still running and the second abandoned - Success" ||
    raise "Incorrect validation result of the two tinyproxies using the same ip and port"  -l "cpm/cpm_same_ip_port.sh" -tc

print_tables Captive_Portal

pass
