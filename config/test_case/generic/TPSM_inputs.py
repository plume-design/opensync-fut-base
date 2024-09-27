test_inputs = {
    "tpsm_crash_speedtest_verify_reporting": {
        "args_mapping": ["test_type", "other_cfg", "extra_step"],
        "inputs": [
            [
                "IPERF3_C",
                {"timeout": 30, "st_dir": "DL", "st_server": "fut.opensync.io", "st_port": 5201},
                "iperf3_server",
            ],
            ["OOKLA", {"kconfig": "CONFIG_3RDPARTY_OOKLA"}, None],
        ],
    },
    "tpsm_verify_iperf3_speedtest": {
        "args_mapping": ["upd", "direction"],
        "inputs": [
            ["false", "DL_UL"],
            ["true", "UL"],
            ["true", "DL"],
        ],
    },
    "tpsm_verify_ookla_speedtest": {},
    "tpsm_verify_ookla_speedtest_bind_options": {},
    "tpsm_verify_ookla_speedtest_bind_reporting": {},
    "tpsm_verify_ookla_speedtest_sdn_endpoint_config": {
        "args_mapping": ["speedtest_config_path"],
        "inputs": ["http://config.speedtest.net/v1/embed/x340jwcv4nz2ou3r/config"],
    },
    "tpsm_verify_samknows_process": {},
}
