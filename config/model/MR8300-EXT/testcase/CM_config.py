test_cfg = {
    "cm2_ble_status_cloud_down": [
        {
            "test_script_timeout": 340,
        },
    ],
    "cm2_ble_status_interface_down": [
        {
            "ignore_collect": True,
            "ignore_collect_msg": "NOT_APPLICABLE: Testcase not applicable for the device",
        },
    ],
    "cm2_ble_status_internet_block": [
        {
        },
    ],
    "cm2_cloud_down": [
        {
            "test_script_timeout": 340,
            "unreachable_cloud_counter": 3,
        },
    ],
    "cm2_dns_failure": [
        {
            "test_script_timeout": 340,
        },
    ],
    "cm2_internet_lost": [
        {
            "test_script_timeout": 340,
            "unreachable_internet_counter": 3,
        },
    ],
    "cm2_link_lost": [
        {
            "test_script_timeout": 340,
        },
    ],
    "cm2_ssl_check": [
        {},
    ],
}
