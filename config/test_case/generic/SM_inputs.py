from config.defaults import def_wifi_args, def_wifi_inputs

def_noise_range_dbm = (-120, 0)
def_sm_args = {
    "sm_report_type": "raw",
    "sm_reporting_count": 0,
    "sm_reporting_interval": 10,
    "sm_sampling_interval": 5,
}

test_inputs = {
    "sm_dynamic_noise_floor": {
        "default": {
            **def_sm_args,
            "mqtt_topic": "sm_dynamic_noise_floor",
            "noise_range_dbm": def_noise_range_dbm,
            "sm_survey_type": "on-chan",
            "stats_type": "survey",
        },
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
    },
    "sm_leaf_report": {
        "default": {
            **def_sm_args,
            "mqtt_topic": "sm_leaf_report",
            "sm_survey_type": "on-chan",
            "stats_type": "client",
        },
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "encryption",
        ],
        "inputs": [
            [6, "HT40", "24g", "WPA2"],
            [44, "HT40", "5g", "WPA2"],
            [44, "HT40", "5gl", "WPA2"],
            [157, "HT40", "5gu", "WPA2"],
            [6, "HT40", "24g", "WPA3"],
            [44, "HT40", "5g", "WPA3"],
            [44, "HT40", "5gl", "WPA3"],
            [157, "HT40", "5gu", "WPA3"],
            [5, "HT40", "6g", "WPA3"],
        ],
    },
    "sm_neighbor_report": {
        "default": {
            **def_sm_args,
            "mqtt_topic": "sm_neighbor_report",
            "neighbors_stats_type": "neighbor",
            "sm_survey_type": "on-chan",
            "survey_stats_type": "survey",
        },
        "args_mapping": [
            "channel",
            "sm_channel",
            "ht_mode",
            "radio_band",
            "encryption",
        ],
        "inputs": [
            [6, 6, "HT40", "24g", "WPA2"],
            [44, 44, "HT40", "5g", "WPA2"],
            [44, 44, "HT40", "5gl", "WPA2"],
            [157, 157, "HT40", "5gu", "WPA2"],
            [6, 6, "HT40", "24g", "WPA3"],
            [44, 44, "HT40", "5g", "WPA3"],
            [44, 44, "HT40", "5gl", "WPA3"],
            [157, 157, "HT40", "5gu", "WPA3"],
            [5, 5, "HT40", "6g", "WPA3"],
        ],
    },
    "sm_survey_report": {
        "default": {
            **def_sm_args,
            "mqtt_topic": "sm_survey_report",
            "stats_type": "survey",
        },
        "args_mapping": [
            "channel",
            "sm_channel",
            "ht_mode",
            "radio_band",
            "encryption",
            "sm_survey_type",
        ],
        "inputs": [
            [6, 6, "HT40", "24g", "WPA2", "on-chan"],
            [44, 44, "HT40", "5g", "WPA2", "on-chan"],
            [44, 44, "HT40", "5gl", "WPA2", "on-chan"],
            [157, 157, "HT40", "5gu", "WPA2", "on-chan"],
            [5, 5, "HT40", "6g", "WPA3", "on-chan"],
            [6, 1, "HT40", "24g", "WPA2", "off-chan"],
            [44, 157, "HT40", "5g", "WPA2", "off-chan"],
            [44, 60, "HT40", "5gl", "WPA2", "off-chan"],
            [157, 108, "HT40", "5gu", "WPA2", "off-chan"],
            [5, 149, "HT40", "6g", "WPA3", "off-chan"],
        ],
    },
}
