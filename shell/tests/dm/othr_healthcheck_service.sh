#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm

usage()
{
cat << usage_string
dm/othr_healthcheck_service.sh [-h] arguments
Description:
    - Script checks if the healthcheck service is correctly installed and running. It checks kconfig for the correct
      configuration option, checks the healthcheck.service file and init.d script are present and if the service is
      running by examining the PID file. It optionally checks individual test scripts, if the inputs are provided, but
      only prints a warning if one of them is not present.
Arguments:
    -h : show this help message
    \$@: names of the individual healthcheck scripts : (strings)(optional)
Script usage example:
    ./dm/othr_healthcheck_service.sh
    ./dm/othr_healthcheck_service.sh "05_ntp.sh" "10_bss.sh" "12_dns.sh" "15_ap.sh" "20_tmp_df.sh" "30_netdev_refcount.sh" "40_conntrack_overflow.sh" "98_file_handles.sh" "99_zombie.sh"
usage_string
}

case "${1}" in
    -h | --help)  usage ; exit 0 ;;
esac

log_title "dm/othr_healthcheck_service.sh: OTHR test - Check if the healthcheck service is correctly configured and running on the device."

check_kconfig_option "CONFIG_SERVICE_HEALTHCHECK" "y" &&
    log "dm/othr_healthcheck_service.sh: healthcheck service is configured on the system - Success" ||
    raise "healthcheck service is not configured on the system" -l "dm/othr_healthcheck_service.sh" -tc

service_file_path="${OPENSYNC_ROOTDIR}/scripts/healthcheck.service"
is_script_on_system ${service_file_path} &&
    log "dm/othr_healthcheck_service.sh: Service file ${service_file_path} is present on the device - Success" ||
    raise "Service file ${service_file_path} is not present on the device" -l "dm/othr_healthcheck_service.sh" -tc

daemon_script_path="/etc/init.d/healthcheck"
is_script_on_system ${daemon_script_path} &&
    log "dm/othr_healthcheck_service.sh: Daemon script ${daemon_script_path} is present on the device - Success" ||
    raise "Daemon script ${daemon_script_path} is not present on the device" -l "dm/othr_healthcheck_service.sh" -tc

script_directory_path="${OPENSYNC_ROOTDIR}/scripts/healthcheck.d"
[ -e ${script_directory_path}/ ] &&
    log "dm/othr_healthcheck_service.sh: Script directory ${script_directory_path} is present on the device - Success" ||
    raise "Script directory ${script_directory_path} is not present on the device" -l "dm/othr_healthcheck_service.sh" -tc

healthcheck_pid_file="/var/run/healthcheck.pid"
[ -e ${healthcheck_pid_file} ] ||
    raise "Healthcheck PID file ${healthcheck_pid_file} is NOT present on the device" -l "dm/othr_healthcheck_service.sh" -tc

healthcheck_pid="$(cat ${healthcheck_pid_file})"
[ -n ${healthcheck_pid} ] &&
    log "dm/othr_healthcheck_service.sh: Healthcheck PID ${healthcheck_pid} - Success" ||
    raise "Healthcheck PID file ${healthcheck_pid_file} is empty" -l "dm/othr_healthcheck_service.sh" -tc

[ -d "/proc/${healthcheck_pid}" ] &&
    log "dm/othr_healthcheck_service.sh: Process file /proc/${healthcheck_pid} exists, healthcheck service is running - Success" ||
    raise "Process file /proc/${healthcheck_pid} does not exist, healthcheck service is not running" -l "dm/othr_healthcheck_service.sh" -tc

for script_name in $@; do
    script_path="${script_directory_path}/${script_name}"
    is_script_on_system ${script_path} &&
        log "dm/othr_healthcheck_service.sh: Daemon script ${script_path} is present on the device - Success" ||
        raise "Daemon script ${script_path} is not present on the device" -l "dm/othr_healthcheck_service.sh" -tc
done

pass
