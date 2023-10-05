#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../..)"

# FUT environment loading
source "${fut_topdir}"/config/default_shell.sh
# Ignore errors for fut_set_env.sh sourcing
[ -e "/tmp/fut-base/fut_set_env.sh" ] && source /tmp/fut-base/fut_set_env.sh &> /dev/null
source "$fut_topdir/lib/rpi_lib.sh"

help()
{
cat << usage_string
Usage: ${MY_NAME} [--help|-h] [--stop|-s]

OPTIONS:
  --help|-h : this help message

Script generates self-signed certificates which are being used for connection to simulated FUT cloud and MQTT broker
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

[ $# -ne 0 ] && help && exit 1

generate_fut_self_signed_certificates
