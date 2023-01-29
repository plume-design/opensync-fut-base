test_inputs = {
    "brv_is_tool_on_system_fut": {
        'additional_inputs': [
            'command',
        ],
    },
    "brv_is_script_on_system_fut": {
        'additional_inputs': [
            "/sys/class/leds/pp203x:red:system/brightness",
            "/sys/class/leds/pp203x:green:system/brightness",
            "/sys/class/leds/pp203x:blue:system/brightness",
        ],
    },
}
