#!/bin/sh

# Reset lib source guards
export FUT_BRV_LIB_SRC=false
export FUT_CM2_LIB_SRC=false
export FUT_DM_LIB_SRC=false
export FUT_NM2_LIB_SRC=false
export FUT_ONBRD_LIB_SRC=false
export FUT_QM_LIB_SRC=false
export FUT_RPI_LIB_SRC=false
export FUT_SM_LIB_SRC=false
export FUT_UM_LIB_SRC=false
export FUT_UNIT_LIB_SRC=false
export FUT_UT_LIB_SRC=false
export FUT_WM2_LIB_SRC=false
export FUT_VPNM_LIB_SRC=false
export FUT_PM_LIB_SRC=false

# Export FUT required env vars if not already set
[ -z "$FUT_TOPDIR" ] && export FUT_TOPDIR="/tmp/fut-base"
[ -z "$OPENSYNC_ROOTDIR" ] && export OPENSYNC_ROOTDIR="/usr/opensync"
[ -z "$LOGREAD" ] && export LOGREAD="cat /var/log/messages"
[ -z "$DEFAULT_WAIT_TIME" ] && export DEFAULT_WAIT_TIME=30
[ -z "$OVSH" ] && export OVSH="${OPENSYNC_ROOTDIR}/tools/ovsh --quiet --timeout=180000"
[ -z "$CAC_TIMEOUT" ] && export CAC_TIMEOUT=60
[ -z "$PLATFORM_OVERRIDE_FILE" ] && export PLATFORM_OVERRIDE_FILE=
[ -z "$MODEL_OVERRIDE_FILE" ] && export MODEL_OVERRIDE_FILE=
[ -z "$PATH" ] && export PATH="/bin:/sbin:/usr/bin:/usr/sbin:${OPENSYNC_ROOTDIR}/tools:${OPENSYNC_ROOTDIR}/bin"
[ -z "$MGMT_IFACE" ] && export MGMT_IFACE=
[ -z "$MGMT_IFACE_UP_TIMEOUT" ] && export MGMT_IFACE_UP_TIMEOUT=10
[ -z "$MGMT_CONN_TIMEOUT" ] && export MGMT_CONN_TIMEOUT=30

echo "${FUT_TOPDIR}/shell/config/default_shell.sh sourced"
