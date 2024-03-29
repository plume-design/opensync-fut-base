test_inputs = {
    "pm_trigger_cloud_logpull": {
        "args_mapping": [
            "upload_location",
            "upload_token",
            "name",
        ],
        "inputs": [
            ["https://fut.opensync.io/logpull.tar.gz", "logpull.tar.gz", "lm"],
        ],
    },
    "pm_verify_log_severity": {
        "args_mapping": [
            "log_severity",
            "name",
        ],
        "inputs": [
            ["TRACE", "NM"],
            ["DEBUG", "WM"],
        ],
    },
}
