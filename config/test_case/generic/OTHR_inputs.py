from config.defaults import def_wifi_args, def_wifi_inputs

test_inputs = {
    "othr_add_client_freeze": {
        "args_mapping": def_wifi_args[:],
        "inputs": def_wifi_inputs,
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
            [6, "HT20", "24g"],
            [44, "HT40", "5g"],
            [44, "HT40", "5gl"],
        ],
    },
    "othr_connect_wifi_client_to_ap": {
        "args_mapping": def_wifi_args[:],
        "inputs": def_wifi_inputs,
    },
    "othr_healthcheck_service": {
        "args_mapping": ["healthcheck_script_list"],
        "inputs": [
            [
                [
                    "05_ntp.sh",
                    "10_bss.sh",
                    "12_dns.sh",
                    "15_ap.sh",
                    "20_tmp_df.sh",
                    "30_netdev_refcount.sh",
                    "40_conntrack_overflow.sh",
                    "98_file_handles.sh",
                    "99_zombie.sh",
                ],
            ],
        ],
    },
    "othr_verify_eth_client_connection": {},
    "othr_verify_eth_lan_iface_wifi_master_state": {},
    "othr_verify_eth_wan_iface_wifi_master_state": {},
    "othr_verify_ethernet_backhaul": {},
    "othr_verify_gre_iface_wifi_master_state": {
        "args_mapping": def_wifi_args[:],
        "inputs": def_wifi_inputs,
    },
    "othr_verify_lan_bridge_iface_wifi_master_state": {},
    "othr_verify_vif_iface_wifi_master_state": {},
    "othr_verify_wan_bridge_iface_wifi_master_state": {},
    "othr_wifi_disabled_after_removing_ap": {
        "args_mapping": def_wifi_args[:],
        "inputs": def_wifi_inputs,
    },
}
