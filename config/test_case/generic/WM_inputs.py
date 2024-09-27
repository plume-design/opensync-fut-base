from config.defaults import (
    all_bandwidth_list,
    all_channels,
    all_encryption_types,
    def_channel_list,
    def_tx_power_set,
    def_wifi_args,
    def_wifi_inputs,
    radio_band_list,
)


bcn_interval_list = [100, 200, 400]

alt_channel_list = [11, 157, 60, 124, 149]
csa_channel_list = [1, 157, 36, 149, 149]
custom_channel_list = [1, 157, 60, 140, 149]
mismatch_channel_list = [36, 1, 157, 36, 3]

mismatch_freq_band = ["5G", "2.4G", "2.4G", "2.4G", "2.4G"]
mismatch_hw_mode = ["11b", "11n", "11n", "11n", "11n"]
mismatch_hw_type = ["randhw3254", "randhw3254", "randhw3254", "randhw3254", "randhw3254"]

alt_bandwidth_list = ["HT20", "HT80", "HT80", "HT80", "HT80"]
mismatch_bandwidth_list = ["HT320", "HT320", "HT320", "HT320", "HT320"]

interface_type_list = ["backhaul_ap", "home_ap", "onboard_ap", "aux_1_ap", "aux_2_ap", "fhaul_ap", "cportal_ap"]
ssid_test_list = [
    "plus+",
    "minus-",
    "asterisk*",
    "hash#",
    "question_mark?",
    "backslash\\",
    "emoji👍",
    "cyrilicГДИѲЛ",
    "arabic٤ټٽ",
    "hebrewאב",
    "japanese飾り羽",
    "georgianბუმბული",
    "special[\\T/]",
    "ssid with spaces",
    "a",
    "а",
    "ssidsbetweenoneandthirtytwobytes",
]

test_inputs = {
    "wm2_check_wpa3_with_wpa2_multi_psk": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_check_wifi_credential_config": {},
    "wm2_connect_wpa3_client": {
        "default": {"encryption": "WPA3"},
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_connect_wpa3_leaf": {
        "default": {"encryption": "WPA3"},
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_create_all_aps_per_radio": {
        "args_mapping": def_wifi_args[:] + ["if_list"],
        "inputs": [
            [6, "HT40", "24g", interface_type_list],
            [44, "HT40", "5g", interface_type_list],
            [44, "HT40", "5gl", interface_type_list],
            [157, "HT40", "5gu", interface_type_list],
        ],
    },
    "wm2_create_wpa3_ap": {
        "default": {"encryption": "WPA3"},
        "args_mapping": def_wifi_args[:] + ["interface_type"],
        "inputs": [sublist[:] + [value] for value in ["home_ap", "backhaul_ap"] for sublist in def_wifi_inputs],
    },
    "wm2_dfs_cac_aborted": {
        "args_mapping": [
            "channel_A",
            "channel_B",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [52, 60, "HT40", "5g"],
            [100, 108, "HT40", "5g"],
            [52, 60, "HT40", "5gl"],
            [100, 108, "HT40", "5gu"],
        ],
    },
    "wm2_ht_mode_and_channel_iteration": {
        "args_mapping": def_wifi_args,
        "inputs": [[ch, bw, rb] for rb in radio_band_list for ch in all_channels[rb] for bw in all_bandwidth_list],
        "do_not_sort": True,
    },
    "wm2_immutable_radio_freq_band": {
        "args_mapping": def_wifi_args[:] + ["freq_band"],
        "inputs": [sublist + [value] for sublist, value in zip(def_wifi_inputs, mismatch_freq_band)],
    },
    "wm2_immutable_radio_hw_mode": {
        "args_mapping": def_wifi_args[:] + ["custom_hw_mode"],
        "inputs": [sublist + [value] for sublist, value in zip(def_wifi_inputs, mismatch_hw_mode)],
    },
    "wm2_immutable_radio_hw_type": {
        "args_mapping": def_wifi_args[:] + ["hw_type"],
        "inputs": [sublist + [value] for sublist, value in zip(def_wifi_inputs, mismatch_hw_type)],
    },
    "wm2_leaf_ht_mode_change": {
        "args_mapping": def_wifi_args[:] + ["custom_ht_mode"],
        "inputs": [sublist + [value] for sublist, value in zip(def_wifi_inputs, alt_bandwidth_list)],
    },
    "wm2_pre_cac_channel_change_validation": {
        "args_mapping": [
            "channel_A",
            "channel_B",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [52, 60, "HT40", "5g"],
            [104, 136, "HT80", "5g"],
            [52, 60, "HT40", "5gl"],
            [104, 136, "HT80", "5gu"],
        ],
    },
    "wm2_pre_cac_ht_mode_change_validation": {
        "args_mapping": [
            "channel",
            "ht_mode_a",
            "ht_mode_b",
            "radio_band",
        ],
        "inputs": [
            [52, "HT80", "HT40", "5g"],
            [52, "HT80", "HT40", "5gl"],
            [104, "HT80", "HT40", "5gu"],
        ],
    },
    "wm2_set_bcn_int": {
        "args_mapping": def_wifi_args[:] + ["bcn_int"],
        "inputs": [sublist + [bcn_interval_list] for sublist in def_wifi_inputs],
        "expand_permutations": True,
    },
    "wm2_set_channel": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_set_channel_neg": {
        "args_mapping": def_wifi_args[:] + ["mismatch_channel"],
        "inputs": [sublist + [value] for sublist, value in zip(def_wifi_inputs, mismatch_channel_list)],
    },
    "wm2_set_ht_mode": {
        "args_mapping": def_wifi_args,
        "inputs": [[ch, bw, rb] for ch, rb in zip(def_channel_list, radio_band_list) for bw in all_bandwidth_list],
    },
    "wm2_set_ht_mode_neg": {
        "args_mapping": def_wifi_args[:] + ["mismatch_ht_mode"],
        "inputs": [sublist + [value] for sublist, value in zip(def_wifi_inputs, mismatch_bandwidth_list)],
    },
    "wm2_set_radio_country": {
        "default": {"country": "US"},
        "args_mapping": ["radio_band"],
        "inputs": radio_band_list[:],
    },
    "wm2_set_radio_thermal_tx_chainmask": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_set_radio_tx_chainmask": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_set_radio_tx_power": {
        "default": {"test_script_timeout": 20},
        "args_mapping": def_wifi_args[:] + ["tx_power"],
        "inputs": [sublist + [list(def_tx_power_set)] for sublist in def_wifi_inputs],
        "expand_permutations": True,
    },
    "wm2_set_radio_tx_power_neg": {
        "default": {
            "test_script_timeout": 20,
            "tx_power": 1,
            "mismatch_tx_power": 32,
        },
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_set_radio_vif_configs": {
        "args_mapping": def_wifi_args[:] + ["custom_channel"],
        "inputs": [sublist + [custom_channel] for sublist, custom_channel in zip(def_wifi_inputs, custom_channel_list)],
    },
    "wm2_set_ssid": {
        "args_mapping": def_wifi_args[:] + ["ssid"],
        "inputs": [sublist + [ssid_test_list] for sublist in def_wifi_inputs],
        "expand_permutations": True,
    },
    "wm2_set_wifi_credential_config": {},
    "wm2_topology_change_change_parent_change_band_change_channel": {
        "default": {"ht_mode": "HT40"},
        "args_mapping": [
            "gw_channel",
            "gw_radio_band",
            "leaf_channel",
            "leaf_radio_band",
        ],
        "inputs": [
            [6, "24g", 44, "5g"],
            [6, "24g", 44, "5gl"],
            [6, "24g", 157, "5gu"],
            [6, "24g", 5, "6g"],
            [44, "5g", 6, "24g"],
            [44, "5g", 5, "6g"],
            [44, "5gl", 6, "24g"],
            [44, "5gl", 157, "5gu"],
            [157, "5gu", 6, "24g"],
            [157, "5gu", 44, "5gl"],
            [5, "6g", 6, "24g"],
            [5, "6g", 44, "5g"],
        ],
    },
    "wm2_topology_change_change_parent_same_band_change_channel": {
        "args_mapping": def_wifi_args[:] + ["leaf_channel"],
        "inputs": [sublist + [leaf_channel] for sublist, leaf_channel in zip(def_wifi_inputs, alt_channel_list)],
    },
    "wm2_topology_change_change_parent_same_band_same_channel": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_transmit_rate_boost": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
        ],
    },
    "wm2_validate_radio_mac_address": {
        "args_mapping": ["radio_band"],
        "inputs": radio_band_list[:],
    },
    "wm2_verify_associated_clients": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_verify_leaf_channel_change": {
        "args_mapping": def_wifi_args[:] + ["csa_channel"],
        "inputs": [sublist + [csa_channel] for sublist, csa_channel in zip(def_wifi_inputs, csa_channel_list)],
    },
    "wm2_verify_gre_tunnel_gw_leaf": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_verify_wifi_security_modes": {
        "args_mapping": def_wifi_args[:] + ["encryption"],
        "inputs": [
            [6, "HT40", "24g", all_encryption_types],
            [44, "HT40", "5g", all_encryption_types],
            [44, "HT40", "5gl", all_encryption_types],
            [157, "HT40", "5gu", all_encryption_types],
            [5, "HT40", "6g", ["WPA3"]],
        ],
        "expand_permutations": True,
    },
    "wm2_wds_backhaul_line_topology": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_wds_backhaul_star_toplogy": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_wds_backhaul_topology_change": {
        "default": {"ht_mode": "HT40"},
        "args_mapping": [
            "gw_channel",
            "gw_radio_band",
            "leaf_channel",
            "leaf_radio_band",
        ],
        "inputs": [
            [6, "24g", 44, "5g"],
            [6, "24g", 44, "5gl"],
            [6, "24g", 157, "5gu"],
            [6, "24g", 5, "6g"],
            [44, "5g", 6, "24g"],
            [44, "5g", 5, "6g"],
            [44, "5gl", 6, "24g"],
            [44, "5gl", 157, "5gu"],
            [157, "5gu", 6, "24g"],
            [157, "5gu", 44, "5gl"],
            [5, "6g", 6, "24g"],
            [5, "6g", 44, "5g"],
        ],
    },
    "wm2_wds_backhaul_traffic_capture": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "wm2_wifi_security_mix_on_multiple_aps": {
        "args_mapping": def_wifi_args[:] + ["encryption_list", "if_list"],
        "inputs": [
            [6, "HT40", "24g", ["WPA2", "WPA3", "open"], interface_type_list],
            [44, "HT40", "5g", ["WPA2", "WPA3", "open"], interface_type_list],
            [44, "HT40", "5gl", ["WPA2", "WPA3", "open"], interface_type_list],
            [157, "HT40", "5gu", ["WPA2", "WPA3", "open"], interface_type_list],
        ],
    },
}
