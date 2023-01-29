test_inputs = {
    "othr_add_client_freeze": {
        'args_mapping': [
            'channel', 'ht_mode', "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_connect_wifi_client_multi_psk": {
        'default': {
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
        },
        'args_mapping': [
            'channel', 'ht_mode', "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_connect_wifi_client_to_ap": {
        'args_mapping': [
            'channel', 'ht_mode', "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_verify_ethernet_backhaul": {},
    "othr_verify_eth_lan_iface_wifi_master_state": {},
    "othr_verify_eth_wan_iface_wifi_master_state": {},
    "othr_verify_gre_iface_wifi_master_state": {
        'args_mapping': [
            'channel', 'ht_mode', "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_verify_gre_tunnel_dut_gw": {
        'args_mapping': [
            'channel', 'ht_mode', "radio_band", "encryption", "wifi_security_type",
        ],
        'inputs': [
            # WPA2
            # 2.4G
            [6, "HT40", "24g", "WPA2", "wpa"],
            # 5G
            [44, "HT40", "5g", "WPA2", "wpa"],
            [157, "HT40", "5g", "WPA2", "wpa"],
            # 5GL
            [44, "HT40", "5gl", "WPA2", "wpa"],
            # 5GU
            [157, "HT40", "5gu", "WPA2", "wpa"],
            # WPA3
            # 2.4G
            [6, "HT40", "24g", "WPA3", "wpa"],
            # 5G
            [44, "HT40", "5g", "WPA3", "wpa"],
            [157, "HT40", "5g", "WPA3", "wpa"],
            # 5GL
            [44, "HT40", "5gl", "WPA3", "wpa"],
            # 5GU
            [157, "HT40", "5gu", "WPA3", "wpa"],
            # 6G
            [5, "HT40", "6g", "WPA3", "wpa"],
            [149, "HT40", "6g", "WPA3", "wpa"],
        ],
    },
    "othr_verify_lan_bridge_iface_wifi_master_state": {},
    "othr_verify_ookla_speedtest": {},
    "othr_verify_samknows_process": {},
    "othr_verify_vif_iface_wifi_master_state": {},
    "othr_verify_wan_bridge_iface_wifi_master_state": {},
    "othr_wifi_disabled_after_removing_ap": {
        'args_mapping': [
            'channel', 'ht_mode', "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "othr_eth_client_connect": {},
}
