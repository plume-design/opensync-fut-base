test_inputs = {
    "brv_is_tool_on_system_fut": {
        "ignore": [
            {
                "inputs": [
                    "radartool",
                    "hciconfig",
                    "exttool",
                    "iwconfig",
                    "iwlist",
                    "iwpriv",
                ],
            },
        ],
    },
    "brv_is_tool_on_system_opensync": {
        "ignore": [
            {
                "inputs": [
                    "base64",
                    "devmem",
                    "lspci",
                ],
            },
        ],
    },
    "brv_busybox_builtins": {
        "ignore": [
            {
                "inputs": [
                    "base64",
                    "devmem",
                    "lspci",
                ],
            },
        ],
    },
    "brv_is_script_on_system_fut": {
        "additional_inputs": [
            "/etc/init.d/wpad",
        ],
        "ignore": [
            {
                "inputs": [
                    "/etc/init.d/qca-hostapd",
                    "/etc/init.d/qca-wpa-supplicant",
                ],
            },
        ],
    },
}
