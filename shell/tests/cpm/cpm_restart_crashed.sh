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
cpm/cpm_restart_crashed.sh [-h] arguments
Description:
    - Script checks that crashed tinyproxies are replaced by new ones
    - Script checks that the newly spawned tinyproxies have same uuids and different pids
Arguments:
    -h : show this help message
Script usage example:
    ./cpm/cpm_restart_crashed.sh
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

spawn_tinyproxies()
{
    insert_ovsdb_entry Captive_Portal \
    -i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
    -i name "default" \
    -i other_config '["map",[["pkt_mark","0x2"]]]' \
    -i proxy_method "reverse" \
    -i uam_url "https://captiveportal1" &&
        log "cpm/cpm_restart_crashed.sh: First Captive_Portal entry inserted - Success" ||
        raise "FAIL: Failed to insert first Captive_Portal entry" -l "cpm/cpm_restart_crashed.sh" -oe

    insert_ovsdb_entry Captive_Portal \
    -i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
    -i name "group" \
    -i other_config '["map",[["pkt_mark","0x2"],["listenip","127.0.0.1"],["listenport","8889"]]]' \
    -i proxy_method "reverse" \
    -i uam_url "https://captiveportal2" &&
        log "cpm/cpm_restart_crashed.sh: Second Captive_Portal entry inserted - Success" ||
        raise "FAIL: Failed to insert second Captive_Portal entry" -l "cpm/cpm_restart_crashed.sh" -oe
}

# create list of <pid>:<uuid> pairs, separated by semicolon (;)
# for example a two item list:
# 25643:93b0ebc3-c89b-484d-a144-ac32c548a19c;25642:f74365a3-9699-4605-ac56-557346b127b0;
create_pid_uuid_list()
{
    pid_uuid_list=""
    pids=$(pidof tinyproxy)
    for pid in $pids
    do
         pid_uuid_list="$pid_uuid_list$pid:"
         uuid=$(cat /proc/$pid/cmdline | grep -Eo "tinyproxy\..*\.conf" | sed 's/tinyproxy\.//' | sed 's/\.conf//')
         pid_uuid_list="$pid_uuid_list$uuid;"
    done
    echo "$pid_uuid_list"
}

store_original_pid_uuid_list()
{
    echo "$1" > /tmp/fut-base/original_pid_uuid_list.txt
}

store_new_pid_uuid_list()
{
    echo "$1" > /tmp/fut-base/new_pid_uuid_list.txt
}

simulate_all_tinyproxies_crash()
{
    init_cpm_test;
    spawn_tinyproxies

    # consider debounce timer 1 second plus 1 second for processes creation
    # 2 seconds are entirely empirical; less was sometimes not enough
    sleep 2

    original_pid_uuid_list="$(create_pid_uuid_list)"
    store_original_pid_uuid_list $original_pid_uuid_list

    killall tinyproxy &&
        log "cpm/cpm_restart_crashed.sh: killed tinyproxy processes - Success" ||
        raise "FAIL: Unable to kill tinyproxy processes"  -l "cpm/cpm_restart_crashed.sh" -tc

    # consider DAEMON_DEFAULT_RESTART_DELAY 1 second plus 1 second for
    # process creation
    sleep 2

    new_pid_uuid_list="$(create_pid_uuid_list)"
    store_new_pid_uuid_list "$new_pid_uuid_list"
}

validate_pid_uuid_lists()
{
    original_pid_uuid_list=$(cat /tmp/fut-base/original_pid_uuid_list.txt)
    if [ -z "$original_pid_uuid_list" ]; then
       raise "Empty original_pid_uuid_list - maybe usleep interval was too short?" -tc
       return 1
    fi
    original_list=$(echo "$original_pid_uuid_list" | sed 's/;/ /g')
    new_pid_uuid_list=$(cat /tmp/fut-base/new_pid_uuid_list.txt)
    new_list=$(echo "$new_pid_uuid_list" | sed 's/;/ /g')

    for original_pid_uuid in $original_list
    do
        retval=1
        original_uuid=${original_pid_uuid#*:} #remove prefix ending in :
        for new_pid_uuid in $new_list
        do
            new_uuid=${new_pid_uuid#*:}
            if [ "$original_uuid" = "$new_uuid" ]; then
                original_pid=${original_pid_uuid%:*} #remove suffix starting with :
                new_pid=${new_pid_uuid%:*}
                # shellcheck disable=SC2086
                if [ -n "$new_pid" ] && [ -n "$original_pid" ] && [ $new_pid != "$original_pid" ]; then
                    retval=0
                    break
                fi
            fi
        done
    done
    return $retval
}

trap '
fut_info_dump_line
print_tables Captive_Portal
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "cpm/cpm_restart_crashed.sh: CPM test - Verify restart of crashed tinyproxies"

simulate_all_tinyproxies_crash

validate_pid_uuid_lists &&
    log "cpm/cpm_restart_crashed.sh: Simulated tinyproxies crash - new pids found - Success" ||
    raise "FAIL: Incorrect tinyproxies crash simulation result"  -l "cpm/cpm_restart_crashed.sh" -tc

print_tables Captive_Portal

pass
