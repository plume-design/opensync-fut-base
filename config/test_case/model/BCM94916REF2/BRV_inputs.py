test_inputs = {
    "brv_is_bcm_license_on_system_fut": {
        "default": {"license_cmd": "bp3 status"},
        "ignore": {
            "inputs": [
                "FULL OVS",
                "FULL SERVICE_QUEUE",
            ],
        },
        "inputs": [
            "BP3_FEATURE_OVS",
            "BP3_FEATURE_SERVICE_QUEUE",
        ],
    },
}
