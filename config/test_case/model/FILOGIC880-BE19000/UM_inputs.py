test_inputs = {
    "um_image": {
        "args_mapping": ["fw_name"],
        "inputs": ["mtkFILOGIC880-BE19000-dsa-10g-spim-nand-squashfs-6.6.0.1-38-g40028d-opensync-dev-debug.bin"],
    },
    "um_corrupt_image": {
        "ignore": {
            "msg": "NOT_APPLICABLE: Detecting a corrupt image is not possible. Skip test to avoid breaking the device.",
        },
    },
}
