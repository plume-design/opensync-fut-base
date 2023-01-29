test_inputs = {
    "wm2_check_wifi_credential_config": [
        {},
    ],
    "wm2_connect_wpa3_client": {
        'default': {
            "wpa_oftags": '["map",[["key","home--1"]]]',
            "wpa_psks": '["map",[["key","home-wpa3-psk"]]]',
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [36, "HT160", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            [36, "HT160", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "wm2_connect_wpa3_leaf": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [36, "HT160", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            [36, "HT160", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "wm2_create_wpa3_ap": {
        'default': {
            "ssid_broadcast": "enabled",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g"],
            # 5G
            [44, "HT40", "5g"],
            [36, "HT160", "5g"],
            [157, "HT40", "5g"],
            # 5GL
            [44, "HT40", "5gl"],
            [36, "HT160", "5gl"],
            # 5GU
            [157, "HT40", "5gu"],
            # 6G
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "wm2_dfs_cac_aborted": {
        'args_mapping': [
            "channel_A", "channel_B", "ht_mode", "radio_band",
        ],
        'inputs': [
            # 5G
            [52, 60, "HT40", "5g"],
            [100, 108, "HT40", "5g"],
            # 5GL
            [52, 60, "HT40", "5gl"],
            # 5GU
            [100, 108, "HT40", "5gu"],
        ],
    },
    "wm2_pre_cac_channel_change_validation": {
        'args_mapping': [
            "channel_A", "channel_B", "ht_mode", "radio_band",
        ],
        'inputs': [
            # 5G
            [52, 60, "HT40", "5g"],
            [40, 60, "HT80", "5g"],
            [104, 136, "HT80", "5g"],
            # 5GL
            [52, 60, "HT40", "5gl"],
            [40, 60, "HT80", "5gl"],
            # 5GU
            [104, 136, "HT80", "5gu"],
        ],
    },
    # Configuration is automatically generated based on device capabilities
    # For each supported radio_band and each ht_mode (until defined max_channel_width) for ALL supported channels
    # For 6G capable devices, list of channel is limited to [1, 9, 21, 57, 101, 125, 149, 157, 197, 213]
    "wm2_ht_mode_and_channel_iteration": {},
    "wm2_immutable_radio_freq_band": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "freq_band",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "5G"],
            # 5G
            [44, "HT40", "5g", "2.4G"],
            [157, "HT40", "5g", "2.4G"],
            # 5GL
            [44, "HT40", "5gl", "2.4G"],
            # 5GU
            [157, "HT40", "5gu", "2.4G"],
            # 6G
            [5, "HT40", "6g", "2.4G"],
            [149, "HT40", "6g", "2.4G"],
        ],
    },
    "wm2_immutable_radio_hw_mode": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "custom_hw_mode",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "11b"],
            # 5G
            [44, "HT40", "5g", "11n"],
            [157, "HT40", "5g", "11n"],
            # 5GL
            [44, "HT40", "5gl", "11n"],
            # 5GU
            [157, "HT40", "5gu", "11n"],
            # 6G
            [5, "HT40", "6g", "11n"],
            [149, "HT40", "6g", "11n"],
        ],
    },
    "wm2_immutable_radio_hw_type": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "hw_type",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "randhw3254"],
            # 5G
            [44, "HT40", "5g", "randhw3254"],
            [157, "HT40", "5g", "randhw3254"],
            # 5GL
            [44, "HT40", "5gl", "randhw3254"],
            # 5GU
            [157, "HT40", "5gu", "randhw3254"],
            # 6G
            [5, "HT40", "6g", "randhw3254"],
            [149, "HT40", "6g", "randhw3254"],
        ],
    },
    "wm2_leaf_ht_mode_change": {
        'args_mapping': [
            'channel', 'ht_mode', "custom_ht_mode", "radio_band", "encryption", "wifi_security_type",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "HT40", "24g", "WPA2", 'wpa'],
            # 5G
            [44, "HT40", "HT80", "5g", "WPA2", 'wpa'],
            [157, "HT40", "HT80", "5g", "WPA2", 'wpa'],
            # 5GL
            [44, "HT40", "HT80", "5gl", "WPA2", 'wpa'],
            # 5GU
            [157, "HT40", "HT80", "5gu", "WPA2", 'wpa'],
            # 6G
            [5, "HT40", "HT80", "6g", "WPA3", 'wpa'],
            [149, "HT40", "HT80", "6g", "WPA3", 'wpa'],
        ],
    },
    "wm2_set_bcn_int": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "bcn_int",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", 400],
            # 5G
            [44, "HT40", "5g", 400],
            [157, "HT40", "5g", 400],
            # 5GL
            [44, "HT40", "5gl", 400],
            # 5GU
            [157, "HT40", "5gu", 400],
            # 6G
            [5, "HT40", "6g", 400],
            [149, "HT40", "6g", 400],
        ],
    },
    # Configuration is automatically generated based on device capabilities
    # For each supported radio_band and ht_mode = HT40 for ALL supported channels
    # For 6G capable devices, list of channel is limited to [5, 21, 37, 53, 69, 85, 101, 117, 133, 149, 165, 181, 197, 213, 229]
    "wm2_set_channel": {},
    "wm2_set_channel_neg": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "mismatch_channels",
        ],
        'inputs': [
            [6, "HT40", "24g", [36, 123]],
            [44, "HT40", "5g", [1, 11]],
            [44, "HT40", "5gl", [1, 157]],
            [157, "HT40", "5g", [1, 11]],
            [157, "HT40", "5gu", [1, 36]],
            [5, "HT40", "6g", [3, 111]],
            [149, "HT40", "6g", [3, 111]],
        ],
    },
    # Configuration is automatically generated based on device capabilities
    # For each supported radio_band and ht_modes for limited list of supported channels
    # For 24G capable devices, list of channel is limited to [1, 6, 11]
    # For 5G capable devices, list of channel is limited to [36, 44, 56, 64, 100, 108, 149, 157]
    # For 5GL capable devices, list of channel is limited to [36, 44, 56, 64]
    # For 5GU capable devices, list of channel is limited to [100, 108, 149, 157]
    # For 6G capable devices, list of channel is limited to [5, 21, 37, 53, 69, 85, 101, 117, 133, 149, 165, 181, 197, 213, 229]
    "wm2_set_ht_mode": {},
    "wm2_set_ht_mode_neg": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "mismatch_ht_mode",
        ],
        'inputs': [
            [6, "HT40", "24g", "HT160"],
            [44, "HT40", "5g", "HT160"],
            [44, "HT40", "5gl", "HT160"],
            [157, "HT40", "5g", "HT160"],
            [157, "HT40", "5gu", "HT160"],
            [5, "HT40", "6g", "HT160"],
            [149, "HT40", "6g", "HT160"],
        ],
    },
    "wm2_set_radio_thermal_tx_chainmask": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "thermal_tx_chainmask", "tx_chainmask",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", 1, 3],
            # 5G
            [44, "HT40", "5g", 1, 3],
            [157, "HT40", "5g", 1, 3],
            # 5GL
            [44, "HT40", "5gl", 1, 3],
            # 5GU
            [157, "HT40", "5gu", 1, 3],
            # 6G
            [5, "HT40", "6g", 1, 3],
            [149, "HT40", "6g", 1, 3],
        ],
    },
    "wm2_set_radio_tx_chainmask": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
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
    "wm2_set_radio_tx_power": {
        'default': {
            "test_script_timeout": 20,
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "tx_powers",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", [1, 6, 23]],
            # 5G
            [44, "HT40", "5g", [1, 6, 23]],
            [157, "HT40", "5g", [1, 6, 23]],
            # 5GL
            [44, "HT40", "5gl", [1, 6, 23]],
            # 5GU
            [157, "HT40", "5gu", [1, 6, 23]],
            # 6G
            [5, "HT40", "6g", [1, 6, 23]],
            [149, "HT40", "6g", [1, 6, 23]],
        ],
    },
    "wm2_set_radio_tx_power_neg": {
        'default': {
            "test_script_timeout": 20,
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "tx_power", "mismatch_tx_power",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", 1, 32],
            # 5G
            [44, "HT40", "5g", 1, 32],
            [157, "HT40", "5g", 1, 32],
            # 5GL
            [44, "HT40", "5gl", 1, 32],
            # 5GU
            [157, "HT40", "5gu", 1, 32],
            # 6G
            [5, "HT40", "6g", 1, 32],
            [149, "HT40", "6g", 1, 32],
        ],
    },
    "wm2_set_radio_vif_configs": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "custom_channel",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", 1],
            # 5G
            [44, "HT40", "5g", 36],
            [157, "HT40", "5g", 149],
            # 5GL
            [44, "HT40", "5gl", 36],
            # 5GU
            [157, "HT40", "5gu", 149],
            # 6G
            [5, "HT40", "6g", 149],
            [149, "HT40", "6g", 5],
        ],
    },
    "wm2_set_ssid": {
        'default': {
            "ssids": [
                "comb1+-*#?",
                "comb2\\👍ИѲЛ٤ټٽ",
                "comb3אב飾り羽[\\T/]",
                "comb4 a",
                "a",
                "ssidsbetweenoneandthirtytwobytes",
            ],
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
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
    "wm2_set_wifi_credential_config": {},
    "wm2_topology_change_change_parent_change_band_change_channel": {
        'args_mapping': [
            "gw_channel", "gw_radio_band", "leaf_channel", "leaf_radio_band", "ht_mode", "wifi_security_type",
        ],
        'inputs': [
            [6, "24g", 44, "5g", "HT40", "wpa"],
            [6, "24g", 149, "5g", "HT40", "wpa"],
            [6, "24g", 44, "5gl", "HT40", "wpa"],
            [6, "24g", 149, "5gu", "HT40", "wpa"],
            [6, "24g", 44, "5gl", "HT40", "wpa"],
            [6, "24g", 149, "5gu", "HT40", "wpa"],
            [6, "24g", 5, "6g", "HT40", "wpa"],
            [6, "24g", 149, "6g", "HT40", "wpa"],
            [44, "5g", 6, "24g", "HT40", "wpa"],
            [44, "5gl", 149, "5gu", "HT40", "wpa"],
            [44, "5g", 5, "6g", "HT40", "wpa"],
            [157, "5g", 6, "24g", "HT40", "wpa"],
            [157, "5gu", 44, "5gl", "HT40", "wpa"],
            [157, "5g", 5, "6g", "HT40", "wpa"],
            [1, "6g", 6, "24g", "HT40", "wpa"],
            [149, "6g", 6, "24g", "HT40", "wpa"],
        ],
    },
    "wm2_topology_change_change_parent_same_band_change_channel": {
        'args_mapping': [
            "gw_channel", "radio_band", "leaf_channel", "ht_mode", "wifi_security_type",
        ],
        'inputs': [
            [6, "24g", 4, "HT40", "wpa"],
            [44, "5g", 48, "HT40", "wpa"],
            [44, "5gl", 48, "HT40", "wpa"],
            [157, "5g", 149, "HT40", "wpa"],
            [157, "5gu", 149, "HT40", "wpa"],
            [5, "6g", 149, "HT40", "wpa"],
            [149, "6g", 5, "HT40", "wpa"],
        ],
    },
    "wm2_topology_change_change_parent_same_band_same_channel": {
        'args_mapping': [
            "channel", "radio_band", "ht_mode", "wifi_security_type",
        ],
        'inputs': [
            [6, "24g", "HT40", "wpa"],
            [44, "5g", "HT40", "wpa"],
            [44, "5gl", "HT40", "wpa"],
            [157, "5g", "HT40", "wpa"],
            [157, "5gu", "HT40", "wpa"],
            [5, "6g", "HT40", "wpa"],
            [149, "6g", "HT40", "wpa"],
        ],
    },
    "wm2_validate_radio_mac_address": {
        'args_mapping': [
            "radio_band",
        ],
        'inputs': [
            "24g",
            "5g",
            "5gl",
            "5gu",
            "6g",
        ],
    },
    "wm2_verify_associated_clients": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
        ],
        'inputs': [
            # 2.4G
            [6, 1, "HT40", "24g"],
            # 5G
            [44, 157, "HT40", "5g"],
            [157, 44, "HT40", "5g"],
            # 5GL
            [44, 36, "HT40", "5gl"],
            # 5GU
            [157, 149, "HT40", "5gu"],
            # 6G
            [5, 149, "HT40", "6g"],
            [149, 5, "HT40", "6g"],
        ],
    },
    "wm2_verify_sta_send_csa": {
        'args_mapping': [
            'channel', 'csa_channel', 'ht_mode', "radio_band", "encryption", "wifi_security_type",
        ],
        'inputs': [
            # 2.4G
            [6, 1, "HT40", "24g", "WPA2", "wpa"],
            # 5G
            [44, 157, "HT40", "5g", "WPA2", "wpa"],
            [157, 44, "HT40", "5g", "WPA2", "wpa"],
            # 5GL
            [44, 36, "HT40", "5gl", "WPA2", "wpa"],
            # 5GU
            [157, 149, "HT40", "5gu", "WPA2", "wpa"],
            # 6G
            [5, 149, "HT40", "6g", "WPA3", "wpa"],
            [149, 5, "HT40", "6g", "WPA3", "wpa"],
        ],
    },
}
