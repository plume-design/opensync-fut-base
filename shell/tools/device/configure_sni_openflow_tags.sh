#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage() {
    cat << usage_string
configure_sni_openflow_tags.sh [-h] arguments
Description:
    - Script configures FSM tag settings to the OVSDB Openflow_Tag table.
    \$1 (mac_gw)          : DUT MAC address         : (string)(required)
    \$2 (mac_client)       : Client MAC address      : (string)(required)
    \$3 (mac_rpi_server)   : RPI server MAC address  : (string)(required)
Arguments:
    -h  show this help message
Script usage example:
    ./configure_sni_openflow_tags.sh <MAC_DUT> <MAC_CLIENT> <MAC_RPI_SERVER>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

trap '
    fut_info_dump_line
    print_tables Openflow_Tag
    fut_info_dump_line
' EXIT INT TERM

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "tools/device/configure_sni_openflow_tags.sh" -arg
mac_gw=${1}
mac_client=${2}
mac_rpi_server=${3}

insert_ovsdb_entry Openflow_Tag \
    -i name all_gateways \
    -i cloud_value ["set",["$mac_gw","$mac_rpi_server"]] &&
        log "configure_sni_openflow_tags.sh: 'all_gateways' inserted to Openflow_Tag - Success" ||
        raise "Failed to insert 'all_gateways' to Openflow_Tag" -l "configure_sni_openflow_tags.sh" -fc

insert_ovsdb_entry Openflow_Tag \
    -i name dpi-devices \
    -i cloud_value ["set",["$mac_client"]] &&
        log "configure_sni_openflow_tags.sh: 'dpi-devices' inserted to Openflow_Tag - Success" ||
        raise "Failed to insert 'dpi-devices' to Openflow_Tag" -l "configure_sni_openflow_tags.sh" -fc

insert_ovsdb_entry Openflow_Tag \
    -i name gateways \
    -i cloud_value ["set",["$mac_rpi_server"]] &&
        log "configure_sni_openflow_tags.sh: 'gateways' inserted to Openflow_Tag - Success" ||
        raise "Failed to insert 'gateways' to Openflow_Tag" -l "configure_sni_openflow_tags.sh" -fc

insert_ovsdb_entry Openflow_Tag \
    -i name walleye_sni_attrs \
    -i cloud_value '["set",["http.host","http.url","tls.sni"]]' &&
        log "configure_sni_openflow_tags.sh: 'walleye_sni_attrs' inserted to Openflow_Tag - Success" ||
        raise "Failed to insert 'walleye_sni_attrs' to Openflow_Tag" -l "configure_sni_openflow_tags.sh" -fc

pass
