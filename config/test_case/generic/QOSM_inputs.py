test_inputs = {
    "qosm_setup": {},
    "qosm_verify_linux_traffic_control_rules": {
        "args_mapping": [
            "egress_action",
            "egress_expected_str",
            "egress_match",
            "if_name",
            "ingress_expected_str_after_update",
            "ingress_expected_str",
            "ingress_action",
            "ingress_match",
            "ingress_updated_match",
            "priority",
        ],
        "inputs": [
            [
                "action mirred egress redirect ",
                "0043",
                "u32 match ip dport 67 0xffff",
                "test-intf",
                "1f90",
                "0050",
                "action mirred egress mirror ",
                "u32 match ip sport 80 0xffff",
                "u32 match ip sport 8080 0xffff",
                11,
            ],
        ],
    },
    "qosm_verify_linux_traffic_control_template_rules": {
        "args_mapping": [
            "egress_action",
            "egress_expected_str",
            "egress_match",
            "egress_match_with_tag",
            "if_name",
            "ingress_action",
            "ingress_match",
            "ingress_tag_name",
        ],
        "inputs": [
            [
                "action mirred egress redirect ",
                "0043",
                "u32 match ip dport 67 0xffff",
                r"u32 match ip dport \${devices_tag} 0xffff",
                "test-intf",
                "action mirred egress mirror ",
                r"u32 match ip dport \${devices_tag} 0xffff",
                "devices_tag",
            ],
        ],
    },
    "qosm_verify_interface_queue": {
        "args_mapping": [
            "test_if_name",
        ],
        "inputs": [
            [
                "dummy_intf1337",
            ],
        ],
    },
    "qosm_verify_linux_queue": {
        "args_mapping": [
            "test_if_name",
        ],
        "inputs": [
            [
                "dummy_intf1337",
            ],
        ],
    },
    "qosm_verify_adaptive_qos": {
        "args_mapping": [
            "test_if_name_up",
            "test_if_name_down",
        ],
        "inputs": [
            [
                "intf1337_up",
                "intf1337_down",
            ],
        ],
    },
}
