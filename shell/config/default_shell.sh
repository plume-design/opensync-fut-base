#!/usr/bin/env sh

# Reset lib source guards
export FUT_BASE_LIB_SRC=false
export FUT_RPI_LIB_SRC=false
export FUT_UNIT_LIB_SRC=false

# Export FUT required env vars if not already set
FUT_TOPDIR=${FUT_TOPDIR:-"/tmp/fut-base"}
MODEL_OVERRIDE_FILE=${MODEL_OVERRIDE_FILE:-"/dev/null"}
OPENSYNC_ROOTDIR=${OPENSYNC_ROOTDIR:-"/usr/opensync"}
OVSH=${OVSH:-"${OPENSYNC_ROOTDIR}/tools/ovsh --quiet --timeout=180000"}
PLATFORM_OVERRIDE_FILE=${PLATFORM_OVERRIDE_FILE:-"/dev/null"}

echo "${FUT_TOPDIR}/shell/config/default_shell.sh sourced"
