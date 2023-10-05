test_inputs = {
    "onbrd_set_and_verify_bridge_mode": {},
    "onbrd_verify_dut_client_certificate_file_on_server": {},
    "onbrd_verify_client_certificate_files": {
        "args_mapping": [
            "cert_file",
        ],
        "inputs": [
            "ca_cert",
            "certificate",
            "private_key",
        ],
    },
    "onbrd_verify_client_tls_connection": {
        "default": {
            "test_script_timeout": 120,
        },
        "args_mapping": [
            "tls_ver",
        ],
        "inputs": [
            "1.2",
        ],
    },
    "onbrd_verify_dhcp_dry_run_success": {
        "inputs": [
            {
                "FutGen|primary-interface-if-name-type": "lan",
            },
        ],
    },
    "onbrd_verify_dut_system_time_accuracy": {
        "default": {
            "time_accuracy": "2",
        },
    },
    "onbrd_verify_fw_version_awlan_node": {
        "default": {
            "search_rule": "pattern_match",
        },
    },
    "onbrd_verify_id_awlan_node": {},
    "onbrd_verify_manager_hostname_resolved": {
        "default": {
            "test_script_timeout": 120,
        },
    },
    "onbrd_verify_model_awlan_node": {},
    "onbrd_verify_number_of_radios": {},
    "onbrd_verify_redirector_address_awlan_node": {},
    "onbrd_verify_router_mode": {
        "args_mapping": [
            "dhcp_end_pool",
            "dhcp_start_pool",
            "gateway_inet_addr",
        ],
        "inputs": [
            ["192.168.40.254", "192.168.40.2", "192.168.40.1"],
        ],
    },
    "onbrd_verify_wan_iface_mac_addr": {},
    "onbrd_verify_wan_ip_address": {},
}
