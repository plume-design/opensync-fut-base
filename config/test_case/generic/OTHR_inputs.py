from config.defaults import def_wifi_args, def_wifi_inputs

test_inputs = {
    "othr_add_client_freeze": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "othr_connect_wifi_client_multi_psk": {
        "default": {
            "psk_a": "multi_psk_a",
            "psk_b": "multi_psk_b",
        },
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "othr_connect_wifi_client_to_ap": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "othr_verify_eth_client_connection": {},
    "othr_verify_eth_lan_iface_wifi_master_state": {},
    "othr_verify_eth_wan_iface_wifi_master_state": {},
    "othr_verify_ethernet_backhaul": {},
    "othr_verify_gre_iface_wifi_master_state": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "othr_verify_lan_bridge_iface_wifi_master_state": {},
    "othr_verify_vif_iface_wifi_master_state": {},
    "othr_verify_wan_bridge_iface_wifi_master_state": {},
    "othr_wifi_disabled_after_removing_ap": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
}
