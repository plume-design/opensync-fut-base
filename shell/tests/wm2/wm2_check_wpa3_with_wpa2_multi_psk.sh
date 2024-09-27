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
wm2/wm2_check_wpa3_with_wpa2_multi_psk.sh [-h] arguments
Description:
    - Moves existing VAP with WPA3 encryption to new radio index and creates new VAP with WPA2 encryption
      on previous radio index.
Arguments:
    -h  show this help message
    -if_name                    : Wifi_Radio_Config::if_name                : (string)(required)
    -bridge                     : Wifi_VIF_Config::bridge                   : (string)(required)
    -enabled                    : Wifi_VIF_Config::enabled                  : (string)(required)
    -primary_vif_if_name        : Wifi_VIF_Config::if_name                  : (string)(required)
    -secondary_vif_if_name      : Wifi_VIF_Config::if_name                  : (string)(required)
    -mode                       : Wifi_VIF_Config::mode                     : (string)(required)
    -primary_ssid               : Wifi_VIF_Config::ssid                     : (string)(required)
    -secondary_ssid             : Wifi_VIF_Config::ssid                     : (string)(required)
    -ssid_broadcast             : Wifi_VIF_Config::broadcast                : (string)(required)
    -primary_vif_radio_idx      : Wifi_VIF_Config::vif_radio_idx            : (string)(required)
    -secondary_vif_radio_idx    : Wifi_VIF_Config::vif_radio_idx            : (string)(required)
    -wpa                        : Wifi_VIF_Config::wpa                      : (string)(required)
    -primary_wpa_key_mgmt       : Wifi_VIF_Config::wpa_key_mgmt             : (string)(required)
    -secondary_wpa_key_mgmt     : Wifi_VIF_Config::wpa_key_mgmt             : (string)(required)
    -primary_wpa_psks           : Wifi_VIF_Config::wpa_psks                 : (string)(required)
    -secondary_wpa_psks         : Wifi_VIF_Config::wpa_psks                 : (string)(required)
    -primary_wpa_oftags         : Wifi_VIF_Config::wpa_oftags               : (string)(required)
    -secondary_wpa_oftags       : Wifi_VIF_Config::wpa_oftags               : (string)(required)
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=36
[ $# -ne ${NARGS} ] && usage && raise "Requires exactly ${NARGS} input argument(s)" -l "wm2/wm2_check_wpa3_with_wpa2_multi_psk.sh" -arg

trap '
    fut_ec=$?
    trap - EXIT INT
    fut_info_dump_line
    print_tables Wifi_Radio_Config Wifi_Radio_State Wifi_VIF_Config Wifi_VIF_State
    fut_info_dump_line
    exit $fut_ec
' EXIT INT TERM

while [ -n "$1" ]; do
    option=$1
    shift
    case "$option" in
        -if_name)
            if_name=${1}
            shift
            ;;
        -bridge)
            bridge=${1}
            shift
            ;;
        -enabled)
            enabled=${1}
            shift
            ;;
        -primary_vif_if_name)
            primary_vif_if_name=${1}
            shift
            ;;
        -secondary_vif_if_name)
            secondary_vif_if_name=${1}
            shift
            ;;
        -mode)
            mode=${1}
            shift
            ;;
        -primary_ssid)
            primary_ssid=${1}
            shift
            ;;
        -secondary_ssid)
            secondary_ssid=${1}
            shift
            ;;
        -ssid_broadcast)
            ssid_broadcast=${1}
            shift
            ;;
        -primary_vif_radio_idx)
            primary_vif_radio_idx=${1}
            shift
            ;;
        -secondary_vif_radio_idx)
            secondary_vif_radio_idx=${1}
            shift
            ;;
        -wpa)
            wpa=${1}
            shift
            ;;
        -primary_wpa_key_mgmt)
            primary_wpa_key_mgmt=${1}
            shift
            ;;
        -secondary_wpa_key_mgmt)
            secondary_wpa_key_mgmt=${1}
            shift
            ;;
        -primary_wpa_psks)
            primary_wpa_psks=${1}
            shift
            ;;
        -secondary_wpa_psks)
            secondary_wpa_psks=${1}
            shift
            ;;
        -primary_wpa_oftags)
            primary_wpa_oftags=${1}
            shift
            ;;
        -secondary_wpa_oftags)
            secondary_wpa_oftags=${1}
            shift
            ;;
        *)
            raise "Wrong option provided: $option" -l "wm2/wm2_check_wpa3_with_wpa2_multi_psk.sh" -arg
            ;;
    esac
done

log_title "wm2/wm2_check_wpa3_with_wpa2_multi_psk.sh: Testing the coexistence of a WPA3 and WPA2 access point on the same radio."

ovsdb_client_command=$(cat <<EOF
[
    "Open_vSwitch",
    {
        "op": "insert",
        "table": "Wifi_VIF_Config",
        "row": {
            "bridge": "${bridge}",
            "enabled": ${enabled},
            "if_name": "${secondary_vif_if_name}",
            "mode": "${mode}",
            "ssid": "${primary_ssid}",
            "ssid_broadcast": "${ssid_broadcast}",
            "vif_radio_idx": ${secondary_vif_radio_idx},
            "wpa": ${wpa},
            "wpa_key_mgmt": "${primary_wpa_key_mgmt}",
            "wpa_oftags": ${primary_wpa_oftags},
            "wpa_psks": ${primary_wpa_psks}
        },
        "uuid-name": "secondary_vif_config"
    },
    {
        "op": "update",
        "table": "Wifi_VIF_Config",
        "where": [
            ["vif_radio_idx", "==", ${primary_vif_radio_idx}]
        ],
        "row": {
            "if_name": "${primary_vif_if_name}",
            "ssid": "${secondary_ssid}",
            "wpa_key_mgmt": "${secondary_wpa_key_mgmt}",
            "wpa_oftags": ${secondary_wpa_oftags},
            "wpa_psks": ${secondary_wpa_psks}
        }
    },
    {
        "op": "mutate",
        "table": "Wifi_Radio_Config",
        "where": [
            ["if_name", "==", "${if_name}"]
        ],
        "mutations": [
            [
                "vif_configs",
                "insert",
                [
                    "set",
                    [
                        ["named-uuid", "secondary_vif_config"]
                    ]
                ]
            ]
        ]
    }
]
EOF
)

ovsdb-client transact "$ovsdb_client_command"

wait_ovsdb_entry Wifi_VIF_State -w if_name "$secondary_vif_if_name" -is vif_radio_idx ${secondary_vif_radio_idx} -is ssid "${primary_ssid}" -is wpa_key_mgmt "$primary_wpa_key_mgmt" &&
    log -deb "wm2:wm2_check_wpa3_with_wpa2_multi_psk - Wifi_VIF_Config reflected to Wifi_VIF_State - Success" ||
    raise "Could not reflect Wifi_VIF_Config to Wifi_VIF_State" -l "wm2:wm2_check_wpa3_with_wpa2_multi_psk" -fc

wait_ovsdb_entry Wifi_VIF_State -w if_name "$primary_vif_if_name"  -is vif_radio_idx ${primary_vif_radio_idx} -is ssid "${secondary_ssid}" -is wpa_key_mgmt "$secondary_wpa_key_mgmt" &&
    log -deb "wm2:wm2_check_wpa3_with_wpa2_multi_psk - Wifi_VIF_Config reflected to Wifi_VIF_State - Success" ||
    raise "Could not reflect Wifi_VIF_Config to Wifi_VIF_State" -l "wm2:wm2_check_wpa3_with_wpa2_multi_psk" -fc
