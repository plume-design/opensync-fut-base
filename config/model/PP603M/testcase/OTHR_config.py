test_cfg = {
    "othr_add_client_freeze": [
        {
            "channel": 2,
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "ht_mode": "HT40",
            "radio_band": "5g",
            "test_script_timeout": 120,
        },
        {
            "channel": 149,
            "ht_mode": "HT40",
            "encryption": "WPA3",
            "radio_band": "6g",
            "test_script_timeout": 120,
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT160",
            "radio_band": "6g",
            "test_script_timeout": 120,
        },
    ],
    "othr_connect_wifi_client_multi_psk": [
        {
            "channel": 6,
            "ht_mode": "HT40",
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "ht_mode": "HT40",
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
            "radio_band": "5g",
        },
        {
            "channel": 48,
            "ht_mode": "HT40",
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
            "radio_band": "5g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
            "radio_band": "6g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT80",
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
            "radio_band": "6g",
        },
    ],
    "othr_connect_wifi_client_to_ap": [
        {
            "channel": 6,
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "ht_mode": "HT40",
            "radio_band": "5g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "radio_band": "6g",
        },
    ],
    "othr_verify_eth_lan_iface_wifi_master_state": [
        {},
    ],
    "othr_verify_eth_wan_iface_wifi_master_state": [
        {},
    ],
    "othr_verify_gre_iface_wifi_master_state": [
        {
            "channel": 6,
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "ht_mode": "HT40",
            "radio_band": "5g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT160",
            "radio_band": "6g",
        },
    ],
    "othr_verify_gre_tunnel_dut_gw": [
        {
            "channel": 6,
            "encryption": "WPA2",
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "encryption": "WPA2",
            "ht_mode": "HT40",
            "radio_band": "5g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT160",
            "radio_band": "6g",
        },
        {
            "channel": 6,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "encryption": "WPA3",
            "ht_mode": "HT40",
            "radio_band": "5g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT160",
            "radio_band": "6g",
        },
    ],
    "othr_verify_iperf3_speedtest": [
        {
            "traffic_type": "forward",
        },
        {
            "traffic_type": "reverse",
        },
        {
            "traffic_type": "udp",
        },
    ],
    "othr_verify_lan_bridge_iface_wifi_master_state": [
        {},
    ],
    "othr_verify_ookla_speedtest": [
        {},
    ],
    "othr_verify_ookla_speedtest_bind_options": [
        {},
    ],
    "othr_verify_ookla_speedtest_bind_reporting": [
        {},
    ],
    "othr_verify_ookla_speedtest_sdn_endpoint_config": [
        {
            "speedtest_config_path": "http://config.speedtest.net/v1/embed/x340jwcv4nz2ou3r/config",
        },
    ],
    "othr_verify_samknows_process": [
        {},
    ],
    "othr_verify_vif_iface_wifi_master_state": [
        {},
    ],
    "othr_verify_wan_bridge_iface_wifi_master_state": [
        {},
    ],
    "othr_wifi_disabled_after_removing_ap": [
        {
            "channel": 6,
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "ht_mode": "HT40",
            "radio_band": "5g",
        },
        {
            "channel": 157,
            "encryption": "WPA3",
            "ht_mode": "HT160",
            "radio_band": "6g",
        },
    ],
}
