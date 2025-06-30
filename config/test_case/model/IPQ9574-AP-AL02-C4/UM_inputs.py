test_inputs = {
    "um_image": {
        "args_mapping": ["fw_name"],
        "inputs": ["qcaALDER_norplusnand-ipq9574-apps-6.6.0-58-gd39470-opensync-dev-debug.img"],
    },
    "um_corrupt_image": {
        "ignore": {
            "msg": "NOT_APPLICABLE: Detecting a corrupt image is not possible. Skip test to avoid breaking the device.",
        },
    },
}
