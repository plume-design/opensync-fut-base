#!/bin/sh

# FUT environment loading
# shellcheck disable=SC1091
source /tmp/fut-base/shell/config/default_shell.sh
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh
source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && source "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && source "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

manager_setup_file="wm2/wm2_setup.sh"

usage()
{
cat << usage_string
wm2/wm2_verify_sta_send_csa_msg.sh [-h] arguments
Description:
    - Script is executed on LEAF device to verify GW sent csa msg on GW channel change
Arguments:
    -h  show this help message
    \$1  (gw_vif_mac)     : GW VIF mac address that LEAF is connected to : (string)(required)
    \$2  (gw_csa_channel) : Channel that triggered CSA on GW             : (string)(required)
    \$3  (ht_mode)        : HT mode of the channel                       : (string)(required)
Testcase procedure:
    - On DEVICE: Run: ./${manager_setup_file} (see ${manager_setup_file} -h)
                 Run: ./wm2/wm2_verify_sta_send_csa_msg.sh <GW_VIF_MAC> <CSA_CHANNEL> <HT_MODE>
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

NARGS=3
[ $# -ne ${NARGS} ] && usage && raise "Requires ${NARGS} input argument(s)" -l "wm2/wm2_verify_sta_send_csa_msg.sh" -arg
gw_vif_mac=${1}
gw_csa_channel=${2}
ht_mode=${3}

log_title "wm2/wm2_verify_sta_send_csa_msg.sh: WM2 test - Verifying sta_send_csa message for MAC ${gw_vif_mac} to channel ${gw_csa_channel}/${ht_mode}"

check_sta_send_csa_message ${gw_vif_mac} ${gw_csa_channel} ${ht_mode} &&
    log "wm2/wm2_verify_sta_send_csa_msg.sh: sta_send_csa message found in logs - Success" ||
    raise "FAIL: Failed to find sta_send_csa message in logs" -l "wm2/wm2_verify_sta_send_csa_msg.sh" -tc

pass
