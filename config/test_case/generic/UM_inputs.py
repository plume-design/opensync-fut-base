test_inputs = {
    "um_corrupt_image": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "um_corrupt_md5_sum": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "um_download_image_while_downloading": {
        "default": {
            "test_script_timeout": 120,
        },
        "args_mapping": [
            "fw_dl_timer",
        ],
        "inputs": [
            30,
        ],
    },
    "um_missing_md5_sum": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "um_set_firmware_url": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "um_set_invalid_firmware_pass": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "um_set_invalid_firmware_url": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "um_set_upgrade_dl_timer_abort": {
        "default": {
            "test_script_timeout": 20,
        },
        "args_mapping": [
            "fw_dl_timer",
        ],
        "inputs": [
            5,
        ],
    },
    "um_set_upgrade_dl_timer_end": {
        "default": {
            "test_script_timeout": 120,
        },
        "args_mapping": [
            "fw_dl_timer",
        ],
        "inputs": [
            100,
        ],
    },
    "um_set_upgrade_timer": {
        "default": {
            "test_script_timeout": 120,
        },
        "args_mapping": [
            "fw_up_timer",
        ],
        "inputs": [
            10,
        ],
    },
    "um_verify_firmware_url_length": {
        "args_mapping": [
            "url_max_length",
        ],
        "inputs": [
            256,
        ],
    },
}
