test_inputs = {
    'dm_verify_node_services': {
        'additional_inputs': [
            ["CONFIG_MANAGER_PSM", "psm"],
        ],
        'ignore': [
            {
                'input': ["CONFIG_MANAGER_PPM", "ppm"],
            },
        ],
    },
    'dm_verify_enable_node_services': {
        'additional_inputs': [
            ["CONFIG_MANAGER_PSM", "psm"],
        ],
        'ignore': [
            {
                'input': ["CONFIG_MANAGER_PPM", "ppm"],
            },
        ],
    },
}
