test_inputs = {
    'dm_verify_counter_inc_reboot_status': {
        'ignore': {
            'msg': "FAIL: PSTORE implementation missing on the device",
        },
    },
    'dm_verify_count_reboot_status': {
        'ignore': {
            'msg': "FAIL: PSTORE implementation missing on the device",
        },
    },
    'dm_verify_reboot_file_exists': {
        'ignore': {
            'msg': "FAIL: Reboot file does not exist",
        },
    },
    'dm_verify_reboot_reason': {
        'ignore': {
            'msg': "FAIL: Reboot file does not exist",
        },
    },
    'dm_verify_node_services': {
        'additional_inputs': [
            ["CONFIG_MANAGER_PSM", "psm"],
        ],
        'ignore': [
            {
                'inputs': [
                    ["CONFIG_MANAGER_PPM", "ppm"],
                    ["CONFIG_MANAGER_BLEM", "blem"],
                    ["CONFIG_MANAGER_CMM", "csc_man"],
                    ["CONFIG_MANAGER_FM", "fm"],
                ],
            },
        ],
    },
    'dm_verify_enable_node_services': {
        'additional_inputs': [
            ["CONFIG_MANAGER_PSM", "psm"],
        ],
        'ignore': [
            {
                'inputs': [
                    ["CONFIG_MANAGER_PPM", "ppm"],
                    ["CONFIG_MANAGER_BLEM", "blem"],
                    ["CONFIG_MANAGER_CMM", "csc_man"],
                    ["CONFIG_MANAGER_FM", "fm"],
                ],
            },
        ],
    },
}
