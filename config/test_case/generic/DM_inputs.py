test_inputs = {
    "dm_verify_awlan_node_params": {
        "args_mapping": [
            "awlan_field_name",
            "awlan_field_val",
        ],
        "inputs": [
            ["firmware_version", "notempty"],
            ["id", "notempty"],
            ["max_backoff", "notempty"],
            ["min_backoff", "notempty"],
            ["model", "notempty"],
            ["revision", "notempty"],
            ["sku_number", "notempty"],
            ["vendor_factory", "notempty"],
            ["vendor_manufacturer", "notempty"],
            ["vendor_mfg_date", "notempty"],
            ["vendor_name", "notempty"],
            ["vendor_part_number", "notempty"],
        ],
        "xfail": [
            {
                "inputs": [
                    ["max_backoff", "notempty"],
                    ["min_backoff", "notempty"],
                    ["revision", "notempty"],
                    ["sku_number", "notempty"],
                    ["vendor_factory", "notempty"],
                    ["vendor_manufacturer", "notempty"],
                    ["vendor_mfg_date", "notempty"],
                    ["vendor_part_number", "notempty"],
                ],
                "msg": "OPTIONAL: AWLAN_Node field not required",
            },
        ],
    },
    "dm_verify_count_reboot_status": {},
    "dm_verify_counter_inc_reboot_status": {},
    "dm_verify_device_mode_awlan_node": {
        "args_mapping": [
            "device_mode",
        ],
        "inputs": [
            "not_set",
        ],
    },
    "dm_verify_enable_node_services": {
        "args_mapping": [
            "kconfig_val",
            "service",
        ],
        "inputs": [
            ["CONFIG_MANAGER_CM", "cm"],
            ["CONFIG_MANAGER_FCM", "fcm"],
            ["CONFIG_MANAGER_FSM", "fsm"],
            ["CONFIG_MANAGER_NM", "nm"],
            ["CONFIG_MANAGER_OM", "om"],
            ["CONFIG_MANAGER_OWM", "owm"],
            ["CONFIG_MANAGER_PM", "pm"],
            ["CONFIG_MANAGER_QM", "qm"],
            ["CONFIG_MANAGER_SM", "sm"],
            ["CONFIG_MANAGER_UM", "um"],
            ["CONFIG_MANAGER_WANO", "wano"],
            ["CONFIG_MANAGER_WM", "wm"],
        ],
    },
    "dm_verify_node_services": {
        "args_mapping": [
            "kconfig_val",
            "service",
        ],
        "inputs": [
            ["CONFIG_MANAGER_CM", "cm"],
            ["CONFIG_MANAGER_FCM", "fcm"],
            ["CONFIG_MANAGER_FSM", "fsm"],
            ["CONFIG_MANAGER_NM", "nm"],
            ["CONFIG_MANAGER_OM", "om"],
            ["CONFIG_MANAGER_OWM", "owm"],
            ["CONFIG_MANAGER_PM", "pm"],
            ["CONFIG_MANAGER_QM", "qm"],
            ["CONFIG_MANAGER_SM", "sm"],
            ["CONFIG_MANAGER_UM", "um"],
            ["CONFIG_MANAGER_WANO", "wano"],
            ["CONFIG_MANAGER_WM", "wm"],
        ],
    },
    "dm_verify_opensync_version_awlan_node": {},
    "dm_verify_reboot_file_exists": {},
    "dm_verify_reboot_reason": {
        "args_mapping": [
            "reboot_reason",
        ],
        "inputs": [
            "USER",
            "CLOUD",
            "COLD_BOOT",
        ],
    },
}
