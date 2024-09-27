from config.defaults import def_wifi_args

test_inputs = {
    "fsm_configure_fsm_tables": {
        "args_mapping": ["handler", "plugin", "tap_name_postfix"],
        "inputs": [
            ["dev_dns", "libfsm_dns.so", "tdns"],
            ["dev_http", "libfsm_http.so", "thttp"],
            ["dev_ndp", "libfsm_ndp.so", "tupnp"],
        ],
    },
    "fsm_configure_openflow_rules": {
        "args_mapping": ["action", "rule", "token"],
        "inputs": [
            ["normal,output:3001", "udp,tp_dst=53", "dev_flow_dns_out"],
            ["normal,output:4001", "tcp,tcp_dst=80", "dev_flow_http_out"],
            ["output:5001", "udp,udp_dst=1900", "dev_flow_upnp_out"],
        ],
    },
    "fsm_configure_test_dpi_http_request": {
        "default": {
            "device_mode": "router",
            "test_client_cmd": "curl http://www.neverssl.com",
            "expected_action": "allowed",
        },
        "args_mapping": def_wifi_args,
        "inputs": [
            [44, "HT40", "5g"],
            [44, "HT40", "5gl"],
        ],
    },
    "fsm_configure_test_dpi_https_sni_request": {
        "default": {
            "device_mode": "router",
            "test_client_cmd": "curl https://www.plume.com",
            "expected_action": "allowed",
        },
        "args_mapping": def_wifi_args,
        "inputs": [
            [36, "HT20", "5g"],
            [36, "HT20", "5gl"],
        ],
    },
    "fsm_configure_test_dpi_http_url_request": {
        "default": {
            "device_mode": "router",
            "test_client_cmd": "curl http://neverssl.com/changes",
            "expected_action": "allowed",
        },
        "args_mapping": def_wifi_args,
        "inputs": [
            [44, "HT40", "5g"],
            [44, "HT40", "5gl"],
        ],
    },
}
