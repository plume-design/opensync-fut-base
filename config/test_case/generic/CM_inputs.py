test_inputs = {
    "cm2_ble_status_cloud_down": {
        "default": {"test_script_timeout": 180},
    },
    "cm2_ble_status_internet_block": {
        "default": {"test_script_timeout": 180},
    },
    "cm2_cloud_down": {
        "default": {"test_script_timeout": 180},
        "args_mapping": ["unreachable_cloud_counter"],
        "inputs": [3],
    },
    "cm2_dns_failure": {
        "default": {"test_script_timeout": 360},
    },
    "cm2_internet_lost": {
        "default": {"test_script_timeout": 180},
        "args_mapping": ["unreachable_internet_counter"],
        "inputs": [3],
    },
    "cm2_link_lost": {
        "default": {"test_script_timeout": 180},
    },
    "cm2_ssl_check": {},
    "cm2_network_outage_link": {
        "default": {"test_script_timeout": 180},
    },
    "cm2_network_outage_router": {
        "default": {"test_script_timeout": 180},
    },
    "cm2_network_outage_internet": {
        "default": {"test_script_timeout": 180},
    },
}
