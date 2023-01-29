test_inputs = {
    "cm2_ble_status_cloud_down": {
        'default': {
            "test_script_timeout": 180,
        },
    },
    "cm2_ble_status_interface_down": {
        'default': {
            "test_script_timeout": 180,
        },
    },
    "cm2_ble_status_internet_block": {
        'default': {
            "test_script_timeout": 180,
        },
    },
    "cm2_cloud_down": {
        'default': {
            "test_script_timeout": 180,
        },
        'inputs': [
            {
                "unreachable_cloud_counter": 3,
            },
        ],
    },
    "cm2_dns_failure": {
        'default': {
            "test_script_timeout": 360,
        },
    },
    "cm2_internet_lost": {
        'default': {
            "test_script_timeout": 180,
        },
        'inputs': [
            {
                "unreachable_internet_counter": 3,
            },
        ],
    },
    "cm2_link_lost": {
        'default': {
            "test_script_timeout": 180,
        },
    },
    "cm2_ssl_check": {},
}
