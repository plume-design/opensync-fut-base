#!/usr/bin/env bash

lib_dir=$(dirname "$(realpath "$BASH_SOURCE")")
export FUT_TOPDIR="$(realpath "$lib_dir"/../..)"
export FUT_CLIENT_LIB_SRC=true
[ "${FUT_UNIT_LIB_SRC}" != true ] && source "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
echo "${FUT_TOPDIR}/shell/lib/client_lib.sh sourced"

####################### INFORMATION SECTION - START ###########################
#
#   Library of common functions to be executed on client devices
#
####################### INFORMATION SECTION - STOP ############################

####################### CLIENT SETUP SECTION - START ############################

####################### CLIENT SETUP SECTION - STOP ############################
