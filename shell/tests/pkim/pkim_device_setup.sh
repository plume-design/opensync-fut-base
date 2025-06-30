#!/bin/sh

[ -e "/tmp/fut-base/fut_set_env.sh" ] && . /tmp/fut-base/fut_set_env.sh
. /tmp/fut-base/shell/config/default_shell.sh
. "${FUT_TOPDIR}/shell/lib/unit_lib.sh"
[ -e "${PLATFORM_OVERRIDE_FILE}" ] && . "${PLATFORM_OVERRIDE_FILE}" || raise "${PLATFORM_OVERRIDE_FILE}" -ofm
[ -e "${MODEL_OVERRIDE_FILE}" ] && . "${MODEL_OVERRIDE_FILE}" || raise "${MODEL_OVERRIDE_FILE}" -ofm
[ -e "${OPENSYNC_ROOTDIR}/etc/kconfig" ]  && . "${OPENSYNC_ROOTDIR}/etc/kconfig" || raise "${OPENSYNC_ROOTDIR}/etc/kconfig" -ofm

TMP_PSTORE="/tmp/pkim-fut/pstore"
TMP_CERTS="/tmp/pkim-fut/certs"

rebind_dir()
{
    src="$1"
    dst="$2"
    umount "$src" || true
    [ -d "$dst" ] && { rm -rf "$dst" || raise "Error cleaning up: $dst" -ds; }
    mkdir -p "$dst" || raise "Unable to create destination folder: $dst" -ds
    tar -C "$src" -c . | tar -C "$dst" -xv || raise "Unable to copy folder $src -> $dst" -ds
    mount "$dst" "$src" || raise "Unable to rebind mount $src -> $dst" -ds
}

pkim_restart()
{
    log "Restarting PKIM ..."
    ovsh u Node_Services --where service==pkim enable:=false
    ovsh wait Node_Services --where service==pkim status:=disabled
    # Erase current configuration
    ovsh d PKI_Config
    ovsh u Node_Services --where service==pkim enable:=true
    ovsh wait Node_Services --where service==pkim status:=enabled
    log "PKIM restarted."
}

rebind_cleanup()
{
    src="$1"
    dst="$2"
    umount "$src" || true
    rm -rf "$dst"
}

pkim_fut_setup()
{
    log "PKIM setup"
    # Rebind the pstore folder to /tmp
    rebind_dir "${CONFIG_PSFS_PRESERVE_DIR}" "${TMP_PSTORE}"
    rebind_dir "${CONFIG_TARGET_PATH_CERT}" "${TMP_CERTS}"
    rm -f "${TMP_PSTORE}/certs" || raise "Unable to remove temporary certs pstore" -ds
    # Enable debug mode
    touch "${CONFIG_TARGET_PATH_CERT}/.debug"
    pkim_restart
}

pkim_fut_cleanup()
{
    log "PKIM cleanup"
    rebind_cleanup "${CONFIG_PSFS_PRESERVE_DIR}" "${TMP_PSTORE}"
    rebind_cleanup "${CONFIG_TARGET_PATH_CERT}" "${TMP_CERTS}"
    pkim_restart
}

case "$1" in
    setup)
        pkim_fut_setup
        ;;
    cleanup)
        pkim_fut_cleanup
        ;;
    *)
        log "Error: Unknown command: $@"
        exit 1
        ;;
esac
