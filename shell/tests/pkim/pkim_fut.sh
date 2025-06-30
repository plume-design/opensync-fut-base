#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm
[ -e "${OPENSYNC_ROOTDIR}/etc/kconfig" ]  && . "${OPENSYNC_ROOTDIR}/etc/kconfig" || raise "${OPENSYNC_ROOTDIR}/etc/kconfig" -ofm

PKIM_SERVER_URL="https://fut.opensync.io:1100"
PKIM_CERT_SERIAL="none"

log()
{
    echo "PKIM_FUT: $@"
}

set -e

pkim_service_stop()
{
    ovsh u Node_Services --where service==pkim enable:=false
    ovsh wait -t 3000 Node_Services --where service==pkim status:=disabled
}

pkim_service_start()
{
    ovsh u Node_Services --where service==pkim enable:=true
    ovsh wait -t 3000 Node_Services --where service==pkim status:=enabled
}

pkim_setup()
{
    pkim_service_stop
    ovsh d PKI_Config
    osps -p erase certs || true
    pkim_service_start
    ovsh i PKI_Config server_url:="$PKIM_SERVER_URL" label:="$1"
}

pkim_renew()
{
    ovsh u PKI_Config --where label==$1 renew:=false
    ovsh u PKI_Config --where label==$1 renew:=true
}

# Normalize a serial number (hex) so its suitable for string comparison:
# - convert lower-case letters to uppercase
# - strip trailing zeroes
ser_normalize()
{
    tr a-z A-Z | sed -e 's/^0*//'
}

#
# Check the serial number of the installed certificate
#
pkim_check_serial()
{
    ESER="$(echo "$PKIM_CERT_SERIAL" | ser_normalize)"
    if [ "$1" == "default" ]
    then
        CERT_PATH="$CONFIG_TARGET_PATH_CERT/$CONFIG_TARGET_PATH_PRIV_CERT"
    else
        CERT_PATH="$CONFIG_TARGET_PATH_CERT/$1/$CONFIG_TARGET_PATH_PRIV_CERT"
    fi
    SER="$(openssl x509 -in "$CERT_PATH" -noout -serial | cut -d '=' -f 2 | ser_normalize)"
    [ "$SER" = "$ESER" ] || {
        log "FAIL: Current serial $CERT_PATH is $SER, expected is $ESER."
        exit 1
    }
    log "Success: Certificate $CERT_PATH serial is $SER."
}

pkim_check_crt_status()
{
    ovsh wait -t 60000 PKI_Config --where label=="$1" status:="$2"
    log "Status: $2"
}

pkim_get_serial()
{
    retry=30
    while [ "$retry" -gt 0 ]
    do
        retry=$((retry - 1))
        sleep 1
        log "Trying server: $PKIM_SERVER_URL [$retry]"
        SER="$(curl -s -k --max-time 60 "$PKIM_SERVER_URL/.well-known/est/fut_params" | grep serial=)" || continue
        PKIM_CERT_SERIAL="$(echo $SER | cut -d= -f2)"
        log "Next certificate serial is: $PKIM_CERT_SERIAL"
        return
    done
    log "Unable to retrieve FUT parameters."
    exit 1
}

case "$1" in
    test_enroll)
        [ -z "$2" ] && { log "Arguments required: label"; exit 1; }
        pkim_get_serial
        pkim_setup "$2"
        pkim_check_crt_status "$2" "success"
        pkim_check_serial "$2"
    ;;
    test_reenroll)
        [ -z "$2" ] && { log "Arguments required: label"; exit 1; }
        pkim_get_serial
        pkim_renew "$2"
        pkim_check_crt_status "$2" "success"
        pkim_check_serial "$2"
    ;;
    test_enroll_overdue)
        [ -z "$2" ] && { log "Arguments required: label"; exit 1; }
        pkim_get_serial
        pkim_setup "$2"
        pkim_check_crt_status "$2" "overdue"
        pkim_check_serial "$2"
    ;;
    test_reenroll_overdue)
        [ -z "$2" ] && { log "Arguments required: label"; exit 1; }
        pkim_get_serial
        pkim_renew "$2"
        pkim_check_crt_status "$2" "overdue"
        pkim_check_serial "$2"
    ;;
    *)
        log "Unknown command: $@"
        exit 1
    ;;
esac
