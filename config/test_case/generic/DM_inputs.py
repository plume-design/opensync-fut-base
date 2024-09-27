from config.defaults import opensync_service_kconfig, opensync_service_name

awlan_node_params_optional = [
    "max_backoff",
    "min_backoff",
    "revision",
    "sku_number",
    "vendor_factory",
    "vendor_manufacturer",
    "vendor_mfg_date",
    "vendor_part_number",
]
awlan_node_params_mandatory = ["firmware_version", "id", "model", "vendor_name"]

test_inputs = {
    "dm_verify_awlan_node_params": {
        "args_mapping": ["awlan_field_name", "awlan_field_val"],
        "inputs": [[item, "notempty"] for item in set(awlan_node_params_mandatory + awlan_node_params_optional)],
        "xfail": {
            "inputs": [[item, "notempty"] for item in awlan_node_params_optional],
            "msg": "OPTIONAL: AWLAN_Node field not required",
        },
    },
    "dm_verify_count_reboot_status": {},
    "dm_verify_counter_inc_reboot_status": {},
    "dm_verify_device_mode_awlan_node": {
        "args_mapping": ["device_mode"],
        "inputs": ["not_set"],
    },
    "dm_verify_enable_node_services": {
        "args_mapping": ["kconfig_val", "service"],
        "inputs": [[kconfig, name] for kconfig, name in zip(opensync_service_kconfig, opensync_service_name)],
    },
    "dm_verify_node_services": {
        "args_mapping": ["kconfig_val", "service"],
        "inputs": [[kconfig, name] for kconfig, name in zip(opensync_service_kconfig, opensync_service_name)],
    },
    "dm_verify_opensync_version_awlan_node": {},
    "dm_verify_reboot_file_exists": {},
    "dm_verify_reboot_reason": {
        "args_mapping": ["reboot_reason"],
        "inputs": ["USER", "CLOUD", "COLD_BOOT"],
    },
}
