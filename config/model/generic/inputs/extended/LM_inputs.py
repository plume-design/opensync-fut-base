test_inputs = {
    "lm_trigger_cloud_logpull": {
        'args_mapping': [
            "upload_location", "upload_token",
        ],
        'inputs': [
            ["https://opensync-development.foo.bar/token12345", "foo12345.tgz"],
        ],
    },
    "lm_verify_log_severity": {
        'args_mapping': [
            "log_severity", "name",
        ],
        'inputs': [
            ["TRACE", "NM"],
            ["DEBUG", "WM"],
        ],
    },
}
