test_inputs = {
    "brv_is_bcm_license_on_system_fut": {
        "default": {"license": "/proc/driver/license"},
        "args_mapping": ["service"],
        "inputs": [
            "FULL OVS",
            "FULL SERVICE_QUEUE",
        ],
    },
    "brv_is_script_on_system_fut": {
        "inputs": ["/etc/init.d/bcm-wlan-drivers.sh"],
    },
    "brv_is_tool_on_system_fut": {
        "inputs": ["wl"],
    },
}
