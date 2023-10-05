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
Usage: $(basename "$0") [--help|-h] [--start] [--stop] [--restart]

OPTIONS:
  --help|-h : this help message
  --start   : start the mosquitto daemon
  --stop    : stop running mosquitto daemons
  --restart : stop running mosquitto daemons (if any) and start the same

Script configures and (re)starts MQTT (mosquitto) that acts as MQTT Broker for FUT.
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

# Clear and or generate fut.mosquitto.log file
echo '' > /tmp/fut.mosquitto.log

ARGS=""
# parse command line arguments
while [[ "${1}" == -* ]]; do
    option="${1}"
    shift
    case "${option}" in
        --start)
            start_fut_mqtt
            exit
            ;;
        --stop)
            stop_fut_mqtt
            exit
            ;;
        --restart)
            stop_fut_mqtt && start_fut_mqtt
            exit
            ;;
    esac
done

help
exit 1
