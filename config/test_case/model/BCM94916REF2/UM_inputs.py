test_inputs = {
    "um_image": {
        "args_mapping": ["fw_name"],
        "inputs": [
            "bcm94916GW+SPU+WLMLO+WL23D2D1GA+BASESHELL+OPENSYNC_nand_squashfs_update_5.04L.04p3-250430_1050-6.6.0-73-gb85028-opensync-dev-debug.pkgtb",
        ],
    },
    "um_corrupt_image": {
        "ignore": {
            "msg": "NOT_APPLICABLE: Detecting a corrupt image is not possible. Skip test to avoid breaking the device.",
        },
    },
}
