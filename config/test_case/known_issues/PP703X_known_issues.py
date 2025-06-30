# Common variables
nm2_set_gateway = {"known_issues": {"msg": "Gateway setting is not removed from Wifi_Inet_State table."}}
wm2_dfs_cac_aborted = {
    "known_issues": {
        "inputs": [
            [52, 60, "HT40", "5g", "WPA3"],
            [100, 108, "HT40", "5g", "WPA3"],
        ],
        "msg": "CAC is not aborted when channel is changed during CAC.",
    },
}
wm2_ht_mode_and_channel_iteration = {
    "known_issues": {
        "inputs": [
            [144, "HT20", "5g", "WPA3"],
            [144, "HT40", "5g", "WPA3"],
        ],
        "msg": "Channel and bandwidth combination does not apply to the radio.",
    },
}
wm2_topology_change_change_parent_change_band_change_channel = {
    "known_issues": {
        "inputs": [
            [5, "6g", 6, "24g"],
            [5, "6g", 44, "5g"],
            [6, "24g", 5, "6g"],
            [6, "24g", 44, "5g"],
            [44, "5g", 5, "6g"],
            [44, "5g", 6, "24g"],
        ],
        "msg": "The osw_confsync has trouble settling sometimes.",
    },
}

known_issues = {
    "6.6.0": {
        "nm2_set_gateway": nm2_set_gateway,
        "wm2_dfs_cac_aborted": wm2_dfs_cac_aborted,
        "wm2_ht_mode_and_channel_iteration": wm2_ht_mode_and_channel_iteration,
        "wm2_topology_change_change_parent_change_band_change_channel": wm2_topology_change_change_parent_change_band_change_channel,
    },
    "7.0.0": {
        "nm2_set_gateway": nm2_set_gateway,
        "wm2_dfs_cac_aborted": wm2_dfs_cac_aborted,
        "wm2_ht_mode_and_channel_iteration": wm2_ht_mode_and_channel_iteration,
    },
}
