test_inputs = {
    "nm2_configure_nonexistent_iface": {
        "args_mapping": [
            "if_name",
            "if_type",
            "inet_addr",
        ],
        "inputs": [
            ["test1", "eth", "10.10.10.15"],
            ["test2", "vif", "10.10.10.16"],
            ["test3", "bridge", "10.10.10.17"],
            ["test4", "tap", "10.10.10.18"],
        ],
    },
    "nm2_configure_verify_native_tap_interface": {
        "args_mapping": [
            "if_type",
            "interface",
        ],
        "inputs": [
            ["tap", "test-intf"],
        ],
    },
    "nm2_enable_disable_iface_network": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "if_name",
            "if_type",
        ],
        "inputs": [
            "FutGen|eth-interfaces",
            [6, "HT40", "24g", "FutGen|vif-bhaul-ap-by-band-and-type"],
            [44, "HT40", "5g", "FutGen|vif-bhaul-ap-by-band-and-type"],
            [44, "HT40", "5gl", "FutGen|vif-bhaul-ap-by-band-and-type"],
            [157, "HT40", "5gu", "FutGen|vif-bhaul-ap-by-band-and-type"],
            [5, "HT40", "6g", "FutGen|vif-bhaul-ap-by-band-and-type"],
        ],
    },
    "nm2_ovsdb_configure_interface_dhcpd": {
        "default": {
            "end_pool": "10.10.10.50",
            "start_pool": "10.10.10.20",
        },
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "if_name",
            "if_type",
        ],
        "inputs": [
            {"FutGen|primary-interface-if-name-type": "lan"},
            [6, "HT40", "24g", "FutGen|vif-home-ap-by-band-and-type"],
            [44, "HT40", "5g", "FutGen|vif-home-ap-by-band-and-type"],
            [157, "HT40", "5g", "FutGen|vif-home-ap-by-band-and-type"],
            [44, "HT40", "5gl", "FutGen|vif-home-ap-by-band-and-type"],
            [157, "HT40", "5gu", "FutGen|vif-home-ap-by-band-and-type"],
            [5, "HT40", "6g", "FutGen|vif-home-ap-by-band-and-type"],
            [149, "HT40", "6g", "FutGen|vif-home-ap-by-band-and-type"],
        ],
    },
    "nm2_ovsdb_ip_port_forward": {
        "default": {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_port": "8080",
            "pf_table": "Netfilter",
        },
        "args_mapping": [
            "src_ifname",
        ],
        "inputs": [
            {"FutGen|eth-interfaces-if-name": "lan"},
            {"FutGen|bridge-interface-if-name": "lan"},
            {"FutGen|vif-interfaces-if-name": "backhaul_sta"},
        ],
    },
    "nm2_ovsdb_remove_reinsert_iface": {
        "inputs": [
            "FutGen|eth-interfaces",
            "FutGen|vif-phy-interfaces",
        ],
    },
    "nm2_set_broadcast": {
        "default": {
            "broadcast": "10.10.10.255",
        },
        "inputs": [
            "FutGen|vif-phy-interfaces",
            {"FutGen|primary-interface-if-name-type": "lan"},
            {"FutGen|primary-interface-if-name-type": "wan"},
        ],
    },
    "nm2_set_dns": {
        "default": {
            "primary_dns": "1.2.3.4",
            "secondary_dns": "4.5.6.7",
        },
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "if_name",
            "if_type",
            "primary_dns",
            "secondary_dns",
        ],
        "inputs": [
            "FutGen|eth-interfaces",
            [6, "HT40", "24g", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.1", "2.2.2.1"],
            [44, "HT40", "5g", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.4", "2.2.2.4"],
            [157, "HT40", "5g", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.8", "2.2.2.8"],
            [44, "HT40", "5gl", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.11", "2.2.2.11"],
            [157, "HT40", "5gu", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.15", "2.2.2.15"],
            [5, "HT40", "6g", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.18", "2.2.2.18"],
            [149, "HT40", "6g", "FutGen|bhaul-sta-by-band-and-type", "1.1.1.22", "2.2.2.22"],
        ],
    },
    "nm2_set_gateway": {
        "default": {
            "gateway": "10.10.10.50",
        },
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "if_name",
            "if_type",
        ],
        "inputs": [
            "FutGen|eth-interfaces",
            [6, "HT40", "24g", "FutGen|vif-home-ap-by-band-and-type"],
            [44, "HT40", "5g", "FutGen|vif-home-ap-by-band-and-type"],
            [157, "HT40", "5g", "FutGen|vif-home-ap-by-band-and-type"],
            [44, "HT40", "5gl", "FutGen|vif-home-ap-by-band-and-type"],
            [157, "HT40", "5gu", "FutGen|vif-home-ap-by-band-and-type"],
            [5, "HT40", "6g", "FutGen|vif-home-ap-by-band-and-type"],
            [149, "HT40", "6g", "FutGen|vif-home-ap-by-band-and-type"],
        ],
    },
    "nm2_set_inet_addr": {
        "default": {
            "inet_addr": "10.10.10.30",
        },
        "inputs": [
            "FutGen|eth-interfaces",
            "FutGen|vif-bhaul-sta-interfaces",
        ],
    },
    "nm2_set_ip_assign_scheme": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
            "ip_assign_scheme",
            "if_name",
            "if_type",
        ],
        "inputs": [
            {
                "FutGen|bridge-interface-if-name-type": "lan",
                "ip_assign_scheme": "dhcp",
            },
            {
                "FutGen|primary-interface-if-name-type": "lan",
                "ip_assign_scheme": "dhcp",
            },
            {
                "FutGen|primary-interface-if-name-type": "wan",
                "ip_assign_scheme": "dhcp",
            },
            [6, "HT40", "24g", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [6, "HT40", "24g", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
            [44, "HT40", "5g", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [157, "HT40", "5g", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [44, "HT40", "5g", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
            [157, "HT40", "5g", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
            [44, "HT40", "5gl", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [44, "HT40", "5gl", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
            [157, "HT40", "5gu", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [157, "HT40", "5gu", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
            [5, "HT40", "6g", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [149, "HT40", "6g", "static", "FutGen|bhaul-sta-by-band-and-type"],
            [5, "HT40", "6g", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
            [149, "HT40", "6g", "dhcp", "FutGen|bhaul-sta-by-band-and-type"],
        ],
    },
    "nm2_set_mtu": {
        "default": {
            "mtu": 1500,
        },
        "inputs": [
            "FutGen|eth-interfaces",
            "FutGen|vif-bhaul-sta-interfaces",
        ],
    },
    "nm2_set_nat": {
        "default": {
            "NAT": "true",
        },
        "inputs": [
            "FutGen|vif-bhaul-sta-interfaces",
            {"FutGen|primary-interface-if-name-type": "wan"},
            {"FutGen|primary-interface-if-name-type": "lan"},
        ],
    },
    "nm2_set_netmask": {
        "default": {
            "netmask": "255.255.0.0",
        },
        "inputs": [
            "FutGen|eth-interfaces",
            "FutGen|vif-bhaul-sta-interfaces",
        ],
    },
    "nm2_set_upnp_mode": {
        "args_mapping": [
            "channel",
            "ht_mode",
            "radio_band",
        ],
        "inputs": [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [157, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "nm2_verify_linux_traffic_control_rules": {
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
    "nm2_verify_linux_traffic_control_template_rules": {
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
    "nm2_verify_native_bridge": {
        "args_mapping": [
            "bridge",
            "interface",
        ],
        "inputs": [
            ["br-test", "test-intf"],
        ],
    },
    "nm2_vlan_interface": {
        "default": {
            "vlan_id": 100,
        },
        "args_mapping": [
            "parent_ifname",
        ],
        "inputs": [
            {"FutGen|primary-interface-if-name": "lan"},
            {"FutGen|primary-interface-if-name": "wan"},
        ],
    },
}
