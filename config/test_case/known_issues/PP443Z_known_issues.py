from config.defaults import (
    all_bandwidths,
    all_channels,
    unii_2,
    unii_2_extended,
)

# Common variables
nm2_set_gateway = {"known_issues": {"msg": "Gateway setting is not removed from Wifi_Inet_State table."}}
wm2_dfs_cac_aborted = {
    "known_issues": {
        "inputs": [
            [52, 60, "HT40", "5gl", "WPA3"],
            [100, 108, "HT40", "5gu", "WPA3"],
        ],
        "msg": "CAC is not aborted when channel is changed during CAC.",
    },
}
wm2_ht_mode_and_channel_iteration = {
    "known_issues": {
        "inputs": [
            [ch, bw, rb, "WPA3"]
            for rb in ["5gl", "5gu"]
            for ch in all_channels[rb]
            if ch in unii_2 + unii_2_extended
            for bw in all_bandwidths
        ],
        "msg": "Test may fail on DFS channels as CAC is not aborted when channel is changed during CAC.",
    },
}
wm2_pre_cac_channel_change_validation = {
    "known_issues": {
        "inputs": [
            [52, 60, "HT40", "5gl", "WPA3"],
            [104, 136, "HT40", "5gu", "WPA3"],
        ],
        "msg": "CAC is not aborted when ht_mode is changed during CAC on the same channel.",
    },
}
wm2_pre_cac_ht_mode_change_validation = {
    "known_issues": {
        "inputs": [
            [52, "HT80", "HT40", "5gl", "WPA3"],
            [104, "HT80", "HT40", "5gu", "WPA3"],
        ],
        "msg": "CAC is not aborted when ht_mode is changed during CAC on the same channel.",
    },
}
wm2_topology_change_change_parent_change_band_change_channel = {
    "known_issues": {
        "inputs": [
            [6, "24g", 44, "5gl"],
            [6, "24g", 157, "5gu"],
            [44, "5gl", 6, "24g"],
            [44, "5gl", 157, "5gu"],
            [157, "5gu", 6, "24g"],
            [157, "5gu", 44, "5gl"],
        ],
        "msg": "The osw_confsync has trouble settling sometimes.",
    },
}

known_issues = {
    "6.6.0": {
        "nm2_set_gateway": nm2_set_gateway,
        "wm2_dfs_cac_aborted": wm2_dfs_cac_aborted,
        "wm2_ht_mode_and_channel_iteration": wm2_ht_mode_and_channel_iteration,
        "wm2_pre_cac_channel_change_validation": wm2_pre_cac_channel_change_validation,
        "wm2_pre_cac_ht_mode_change_validation": wm2_pre_cac_ht_mode_change_validation,
        "wm2_topology_change_change_parent_change_band_change_channel": wm2_topology_change_change_parent_change_band_change_channel,
    },
}
