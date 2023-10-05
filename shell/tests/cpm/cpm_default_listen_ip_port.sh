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
cpm/cpm_default_listen_ip_port.sh [-h] arguments
Description:
    - Script checks that the correct listenip and listenport values are set in the tinyproxy config file
Arguments:
    -h : show this help message
Script usage example:
    ./cpm/cpm_default_listen_ip_port.sh
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

validate_tinyproxy_ip_port()
{
    retval=1
    uuid=$(get_ovsdb_entry_value Captive_Portal _uuid -w name "default")
    listenip=$(cat /tmp/tinyproxy/tinyproxy."$uuid".conf | grep "Listen .*" | sed 's/Listen //')
    listenport=$(cat /tmp/tinyproxy/tinyproxy."$uuid".conf | grep "port .*" | sed 's/port //')
    echo "uuid, ip and port: $uuid, $listenip, $listenport"
    [ "$listenip" = "127.0.0.1" ] && [ "$listenport" = "8888" ] && retval=0
    return $retval
}

trap '
fut_info_dump_line
print_tables Captive_Portal
echo "Final tinyproxies status:"
ps -w | grep tinyproxy | grep -v grep
echo "listenip and listenport in the config file:"
grep -rn "Listen " /tmp/tinyproxy
grep -rn "port " /tmp/tinyproxy
check_restore_ovsdb_server
fut_info_dump_line
' EXIT SIGINT SIGTERM

log_title "cpm/cpm_default_listen_ip_port.sh: CPM test - Verify default listen ip and port"

init_cpm_test

insert_ovsdb_entry Captive_Portal \
    -i additional_headers '["map",[["X-LocationID","100000000000000000000001"],["X-PodID","1000000001"],["X-PodMac","aa:bb:cc:dd:ee:ff"],["X-SSID","FUT_ssid_guest"]]]' \
    -i name "default" \
    -i other_config '["map",[["pkt_mark","0x2"]]]' \
    -i proxy_method "reverse" \
    -i uam_url "https://captiveportal1" &&
        log "cpm/cpm_default_listen_ip_port.sh: First Captive_Portal entry inserted - Success" ||
        raise "FAIL: Failed to insert first Captive_Portal entry" -l "cpm/cpm_default_listen_ip_port.sh" -oe

# debounce timer 1 second plus one additional second
sleep 2

validate_tinyproxy_ip_port &&
    log "cpm/cpm_default_listen_ip_port.sh: Found Listen 127.0.0.1 and port 8888 - Success" ||
    raise "FAIL: incorrect tinyproxy config listen and port values"  -l "cpm/cpm_default_listen_ip_port.sh" -tc

print_tables Captive_Portal

pass
