test_inputs = {
    'dm_verify_node_services': {
        'additional_inputs': [
            ["CONFIG_MANAGER_PSM", "psm"],
        ],
        'ignore': [
            {
                'inputs': [
                    ["CONFIG_MANAGER_PPM", "ppm"],
                    ["CONFIG_MANAGER_BLEM", "blem"],
                    ["CONFIG_MANAGER_FM", "fm"],
                    ["CONFIG_MANAGER_UM", "um"],
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
                    ["CONFIG_MANAGER_FM", "fm"],
                    ["CONFIG_MANAGER_UM", "um"],
                ],
            },
        ],
    },
}
