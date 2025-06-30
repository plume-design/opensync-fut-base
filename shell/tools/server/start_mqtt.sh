#!/usr/bin/env bash

current_dir=$(dirname "$(realpath "$BASH_SOURCE")")
fut_topdir="$(realpath "$current_dir"/../../..)"
source "${fut_topdir}/shell/lib/rpi_lib.sh"

usage()
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
    -h | --help) usage ; exit 0 ;;
esac

trap '
    fut_ec=$?
    trap - EXIT INT
    pgrep mosquitto
    cat /tmp/fut.mosquitto.log
    exit $fut_ec
' EXIT INT TERM

# Clear and or generate fut.mosquitto.log file
echo '' > /tmp/fut.mosquitto.log

# parse command line arguments
while [[ "${1}" == -* ]]; do
    option="${1}"
    shift
    case "${option}" in
        --start)
            start_fut_mqtt
            ;;
        --stop)
            stop_fut_mqtt
            ;;
        --restart)
            stop_fut_mqtt
            sleep 1
            start_fut_mqtt
            ;;
    esac
done
