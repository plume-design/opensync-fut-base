test_inputs = {
    "sm_leaf_report": {
        'default': {
            "sm_report_type": "raw",
            "sm_reporting_interval": 10,
            "sm_sampling_interval": 5,
            "sm_survey_type": "on-chan",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "sm_radio_type", "encryption", "wifi_security_type",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "2.4G", "WPA2", "wpa"],
            # 5G
            [44, "HT40", "5g", "5G", "WPA2", "wpa"],
            [157, "HT40", "5g", "5G", "WPA2", "wpa"],
            # 5GL
            [44, "HT40", "5gl", "5GL", "WPA2", "wpa"],
            # 5GU
            [157, "HT40", "5gu", "5GU", "WPA2", "wpa"],
            # 2.4G
            [6, "HT40", "24g", "2.4G", "WPA3", "wpa"],
            # 5G
            [44, "HT40", "5g", "5G", "WPA3", "wpa"],
            [157, "HT40", "5g", "5G", "WPA3", "wpa"],
            # 5GL
            [44, "HT40", "5gl", "5GL", "WPA3", "wpa"],
            # 5GU
            [157, "HT40", "5gu", "5GU", "WPA3", "wpa"],
            # 6G
            [5, "HT40", "6g", "6G", "WPA3", "wpa"],
            [149, "HT40", "6g", "6G", "WPA3", "wpa"],
        ],
    },
    "sm_neighbor_report": {
        'default': {
            "sm_report_type": "raw",
            "sm_reporting_interval": 10,
            "sm_sampling_interval": 5,
            "sm_survey_type": "on-chan",
        },
        'args_mapping': [
            "channel", "sm_channel", "ht_mode", "radio_band", "sm_radio_type", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, 6, "HT40", "24g", "2.4G", "WPA2"],
            # 5G
            [44, 44, "HT40", "5g", "5G", "WPA2"],
            [157, 157, "HT40", "5g", "5G", "WPA2"],
            # 5GL
            [44, 44, "HT40", "5gl", "5GL", "WPA2"],
            # 5GU
            [157, 157, "HT40", "5gu", "5GU", "WPA2"],
            # 2.4G
            [6, 6, "HT40", "24g", "2.4G", "WPA3"],
            # 5G
            [44, 44, "HT40", "5g", "5G", "WPA3"],
            [157, 157, "HT40", "5g", "5G", "WPA3"],
            # 5GL
            [44, 44, "HT40", "5gl", "5GL", "WPA3"],
            # 5GU
            [157, 157, "HT40", "5gu", "5GU", "WPA3"],
            # 6G
            [5, 5, "HT40", "6g", "6G", "WPA3"],
            [149, 149, "HT40", "6g", "6G", "WPA3"],
        ],
    },
    "sm_survey_report": {
        'default': {
            "sm_report_type": "raw",
            "sm_reporting_interval": 10,
            "sm_sampling_interval": 5,
        },
        'args_mapping': [
            "channel", "sm_channel", "ht_mode", "radio_band", "sm_radio_type", "encryption", "sm_survey_type",
        ],
        'inputs': [
            # on-chan
            # 2.4G
            [6, 6, "HT40", "24g", "2.4G", "WPA2", 'on-chan'],
            # 5G
            [44, 44, "HT40", "5g", "5G", "WPA2", 'on-chan'],
            [157, 157, "HT40", "5g", "5G", "WPA2", 'on-chan'],
            # 5GL
            [44, 44, "HT40", "5gl", "5GL", "WPA2", 'on-chan'],
            # 5GU
            [157, 157, "HT40", "5gu", "5GU", "WPA2", 'on-chan'],
            # 6G
            [5, 5, "HT40", "6g", "6G", "WPA3", 'on-chan'],
            [149, 149, "HT40", "6g", "6G", "WPA3", 'on-chan'],
            # off-chan
            # 2.4G
            [6, 1, "HT40", "24g", "2.4G", "WPA2", 'off-chan'],
            # 5G
            [44, 36, "HT40", "5g", "5G", "WPA2", 'off-chan'],
            [157, 149, "HT40", "5g", "5G", "WPA2", 'off-chan'],
            # 5GL
            [44, 36, "HT40", "5gl", "5GL", "WPA2", 'off-chan'],
            # 5GU
            [157, 149, "HT40", "5gu", "5GU", "WPA2", 'off-chan'],
            # 6G
            [5, 149, "HT40", "6g", "6G", "WPA3", 'off-chan'],
            [149, 5, "HT40", "6g", "6G", "WPA3", 'off-chan'],
        ],
    },
}
