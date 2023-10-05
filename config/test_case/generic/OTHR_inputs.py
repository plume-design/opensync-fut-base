test_inputs = {
    "othr_add_client_freeze": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_connect_wifi_client_multi_psk": {
        "default": {
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
        },
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_connect_wifi_client_to_ap": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_verify_eth_client_connection": {},
    "othr_verify_eth_lan_iface_wifi_master_state": {},
    "othr_verify_eth_wan_iface_wifi_master_state": {},
    "othr_verify_ethernet_backhaul": {},
    "othr_verify_gre_iface_wifi_master_state": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_verify_gre_tunnel_dut_gw": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "encryption",
            "wifi_security_type",
        ],
        "inputs": [
            [6, "HT40", "24g", "WPA2", "wpa"],
            [44, "HT40", "5g", "WPA2", "wpa"],
            [157, "HT40", "5g", "WPA2", "wpa"],
            [44, "HT40", "5gl", "WPA2", "wpa"],
            [157, "HT40", "5gu", "WPA2", "wpa"],
            [6, "HT40", "24g", "WPA3", "wpa"],
            [44, "HT40", "5g", "WPA3", "wpa"],
            [157, "HT40", "5g", "WPA3", "wpa"],
            [44, "HT40", "5gl", "WPA3", "wpa"],
            [157, "HT40", "5gu", "WPA3", "wpa"],
            [5, "HT40", "6g", "WPA3", "wpa"],
            [149, "HT40", "6g", "WPA3", "wpa"],
        ],
    },
    "othr_verify_iperf3_speedtest": {
        "args_mapping": [
            "traffic_type",
        ],
        "inputs": [
            "forward",
            "reverse",
            "udp",
        ],
    },
    "othr_verify_lan_bridge_iface_wifi_master_state": {},
    "othr_verify_ookla_speedtest": {},
    "othr_verify_ookla_speedtest_bind_options": {},
    "othr_verify_ookla_speedtest_bind_reporting": {},
    "othr_verify_ookla_speedtest_sdn_endpoint_config": {
        "args_mapping": [
            "speedtest_config_path",
        ],
        "inputs": [
            "http://config.speedtest.net/v1/embed/x340jwcv4nz2ou3r/config",
        ],
    },
    "othr_verify_samknows_process": {},
    "othr_verify_vif_iface_wifi_master_state": {},
    "othr_verify_wan_bridge_iface_wifi_master_state": {},
    "othr_wifi_disabled_after_removing_ap": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
}
