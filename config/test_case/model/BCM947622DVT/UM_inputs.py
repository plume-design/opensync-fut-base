test_inputs = {
    "um_image": {
        "args_mapping": ["fw_name"],
        "inputs": [
            "bcm947622GW+BASESHELL+OPENSYNC+IMPL87_nand_squashfs_update_5.04L.02p1-231020_2012-5.6.0.0-321-g9c153c-opensync-dev-debug.pkgtb",
        ],
    },
    "um_corrupt_image": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_corrupt_md5_sum": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_download_image_while_downloading": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_missing_md5_sum": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_set_firmware_url": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_set_invalid_firmware_pass": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_set_invalid_firmware_url": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_set_upgrade_dl_timer_abort": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_set_upgrade_dl_timer_end": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_set_upgrade_timer": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
    "um_verify_firmware_url_length": {
        "ignore": {"msg": "NOT_APPLICABLE: UM tests are not applicable to reference boards"},
    },
}
