test_inputs = {
    "fsm_configure_fsm_tables": {
        'args_mapping': [
            "handler", "plugin", "tap_name_postfix",
        ],
        'inputs': [
            ["dev_dns", "libfsm_dns.so", "tdns"],
            ["dev_http", "libfsm_http.so", "thttp"],
            ["dev_ndp", "libfsm_ndp.so", "tupnp"],
        ],
    },
    "fsm_configure_openflow_rules": {
        'args_mapping': [
            "action", "rule", "token",
        ],
        'inputs': [
            ["normal,output:3001", "udp,tp_dst=53", "dev_flow_dns_out"],
            ["normal,output:4001", "tcp,tcp_dst=80", "dev_flow_http_out"],
            ["output:5001", "udp,udp_dst=1900", "dev_flow_upnp_out"],
        ],
    },
    "fsm_configure_test_dns_plugin": {
        'default': {
            "plugin": "libfsm_dns.so",
            "plugin_web_cat": "libfsm_wcnull.so",
            "url_block": "google.com",
            "url_redirect": "1.2.3.4",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "device_mode", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "router", "WPA2"],
            # 5G
            [48, "HT40", "5g", "router", "WPA2"],
            [157, "HT40", "5g", "router", "WPA2"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA2"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA2"],
            # 2.4G
            [6, "HT40", "24g", "router", "WPA3"],
            # 5G
            [48, "HT40", "5g", "router", "WPA3"],
            [157, "HT40", "5g", "router", "WPA3"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA3"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA3"],
            # 6G
            [5, "HT40", "6g", "router", "WPA3"],
            [149, "HT40", "6g", "router", "WPA3"],
        ],
    },
    "fsm_configure_test_dpi_http_request": {
        'default': {
            "plugin_gk": "libfsm_gatekeeper.so",
            "plugin_dpi_sni": "libfsm_dpi_sni.so",
            "url": "http://www.neverssl.com",
            "verdict": "allowed",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "device_mode", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "router", "WPA2"],
            # 5G
            [48, "HT40", "5g", "router", "WPA2"],
            [157, "HT40", "5g", "router", "WPA2"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA2"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA2"],
            # 2.4G
            [6, "HT40", "24g", "router", "WPA3"],
            # 5G
            [48, "HT40", "5g", "router", "WPA3"],
            [157, "HT40", "5g", "router", "WPA3"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA3"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA3"],
            # 6G
            [5, "HT40", "6g", "router", "WPA3"],
            [149, "HT40", "6g", "router", "WPA3"],
        ],
    },
    "fsm_configure_test_dpi_http_url_request": {
        'default': {
            "plugin_gk": "libfsm_gatekeeper.so",
            "plugin_dpi_sni": "libfsm_dpi_sni.so",
            "url": "http://www.neverssl.com/changes",
            "verdict": "allowed",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "device_mode", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "router", "WPA2"],
            # 5G
            [48, "HT40", "5g", "router", "WPA2"],
            [157, "HT40", "5g", "router", "WPA2"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA2"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA2"],
            # 2.4G
            [6, "HT40", "24g", "router", "WPA3"],
            # 5G
            [48, "HT40", "5g", "router", "WPA3"],
            [157, "HT40", "5g", "router", "WPA3"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA3"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA3"],
            # 6G
            [5, "HT40", "6g", "router", "WPA3"],
            [149, "HT40", "6g", "router", "WPA3"],
        ],
    },
    "fsm_configure_test_http_plugin": {
        'default': {
            "plugin": "libfsm_http.so",
            "user_agent": "fsm_http_user_agent",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "device_mode", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "router", "WPA2"],
            # 5G
            [48, "HT40", "5g", "router", "WPA2"],
            [157, "HT40", "5g", "router", "WPA2"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA2"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA2"],
            # 2.4G
            [6, "HT40", "24g", "router", "WPA3"],
            # 5G
            [48, "HT40", "5g", "router", "WPA3"],
            [157, "HT40", "5g", "router", "WPA3"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA3"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA3"],
            # 6G
            [5, "HT40", "6g", "router", "WPA3"],
            [149, "HT40", "6g", "router", "WPA3"],
        ],
    },
    "fsm_configure_test_ndp_plugin": {
        'default': {
            "plugin": "libfsm_ndp.so",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "device_mode", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "router", "WPA2"],
            # 5G
            [48, "HT40", "5g", "router", "WPA2"],
            [157, "HT40", "5g", "router", "WPA2"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA2"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA2"],
            # 2.4G
            [6, "HT40", "24g", "router", "WPA3"],
            # 5G
            [48, "HT40", "5g", "router", "WPA3"],
            [157, "HT40", "5g", "router", "WPA3"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA3"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA3"],
            # 6G
            [5, "HT40", "6g", "router", "WPA3"],
            [149, "HT40", "6g", "router", "WPA3"],
        ],
    },
    "fsm_configure_test_upnp_plugin": {
        'default': {
            "plugin": "libfsm_upnp.so",
            "upnp_device_type": "urn:plume-test:device:test:1",
            "upnp_friendly_name": "FUT test device",
            "upnp_manufacturer": "FUT testing, Inc",
            "upnp_manufacturer_URL": "https://www.fut.com",
            "upnp_model_description": "FUT UPnP service",
            "upnp_model_name": "FUT tester",
            "upnp_model_number": "1.0",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "device_mode", "encryption",
        ],
        'inputs': [
            # 2.4G
            [6, "HT40", "24g", "router", "WPA2"],
            # 5G
            [48, "HT40", "5g", "router", "WPA2"],
            [157, "HT40", "5g", "router", "WPA2"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA2"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA2"],
            # 2.4G
            [6, "HT40", "24g", "router", "WPA3"],
            # 5G
            [48, "HT40", "5g", "router", "WPA3"],
            [157, "HT40", "5g", "router", "WPA3"],
            # 5GL
            [48, "HT40", "5gl", "router", "WPA3"],
            # 5GU
            [157, "HT40", "5gu", "router", "WPA3"],
            # 6G
            [5, "HT40", "6g", "router", "WPA3"],
            [149, "HT40", "6g", "router", "WPA3"],
        ],
    },
    "fsm_configure_test_walleye_plugin": {
        'default': {
            "plugin": "libfsm_walleye_dpi.so",
        },
    },
    "fsm_create_tap_interface": {
        'args_mapping': [
            "of_port", "tap_name_postfix",
        ],
        'inputs': [
            [3001, "tdns"],
            [4001, "thttp"],
            [5001, "tupnp"],
        ],
    },
}
