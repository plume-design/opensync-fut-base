from config.defaults import def_wifi_args, def_wifi_inputs

test_inputs = {
    "nm2_configure_nonexistent_iface": {
        "args_mapping": ["if_name", "if_type", "inet_addr"],
        "inputs": [
            ["test1", "eth", "10.10.10.15"],
            ["test2", "vif", "10.10.10.16"],
            ["test3", "bridge", "10.10.10.17"],
        ],
    },
    "nm2_configure_verify_native_tap_interface": {
        "args_mapping": ["if_name", "if_type"],
        "inputs": [
            ["test-intf", "tap"],
        ],
    },
    "nm2_enable_disable_iface_network": {
        "args_mapping": ["channel", "ht_mode", "radio_band", "if_role"],
        "inputs": [
            [None, None, None, "lan_interfaces"],
            [6, "HT40", "24g", "backhaul_ap"],
            [44, "HT40", "5g", "backhaul_ap"],
            [44, "HT40", "5gl", "backhaul_ap"],
            [157, "HT40", "5gu", "backhaul_ap"],
            [5, "HT40", "6g", "backhaul_ap"],
        ],
    },
    "nm2_ovsdb_configure_interface_dhcpd": {
        "default": {
            "end_pool": "10.10.10.50",
            "start_pool": "10.10.10.20",
        },
        "args_mapping": ["channel", "ht_mode", "radio_band", "if_role"],
        "inputs": [
            [None, None, None, "primary_lan_interface"],
            [6, "HT40", "24g", "home_ap"],
            [44, "HT40", "5g", "home_ap"],
            [44, "HT40", "5gl", "home_ap"],
            [157, "HT40", "5gu", "home_ap"],
            [5, "HT40", "6g", "home_ap"],
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
        "args_mapping": ["if_role"],
        "inputs": [
            ["lan_interfaces"],
            ["lan_bridge"],
            ["backhaul_sta"],
        ],
    },
    "nm2_ovsdb_remove_reinsert_iface": {
        "args_mapping": ["if_role"],
        "inputs": [
            ["lan_interfaces"],
        ],
    },
    "nm2_set_broadcast": {
        "default": {
            "broadcast": "10.10.10.255",
        },
        "args_mapping": ["if_role"],
        "inputs": [
            ["primary_lan_interface"],
            ["primary_wan_interface"],
        ],
    },
    "nm2_set_dns": {
        "default": {
            "primary_dns": "1.2.3.4",
            "secondary_dns": "4.5.6.7",
        },
        "args_mapping": ["channel", "ht_mode", "radio_band", "primary_dns", "secondary_dns", "if_role"],
        "inputs": [
            [None, None, None, None, None, "lan_interfaces"],
            [6, "HT40", "24g", "1.1.1.1", "2.2.2.1", "backhaul_sta"],
            [44, "HT40", "5g", "1.1.1.4", "2.2.2.4", "backhaul_sta"],
            [44, "HT40", "5gl", "1.1.1.11", "2.2.2.11", "backhaul_sta"],
            [157, "HT40", "5gu", "1.1.1.15", "2.2.2.15", "backhaul_sta"],
            [5, "HT40", "6g", "1.1.1.18", "2.2.2.18", "backhaul_sta"],
        ],
    },
    "nm2_set_gateway": {
        "default": {
            "gateway": "10.10.10.50",
        },
        "args_mapping": ["channel", "ht_mode", "radio_band", "if_role"],
        "inputs": [
            [None, None, None, "lan_interfaces"],
            [6, "HT40", "24g", "home_ap"],
            [44, "HT40", "5g", "home_ap"],
            [44, "HT40", "5gl", "home_ap"],
            [157, "HT40", "5gu", "home_ap"],
            [5, "HT40", "6g", "home_ap"],
        ],
    },
    "nm2_set_inet_addr": {
        "default": {
            "inet_addr": "10.10.10.30",
        },
        "args_mapping": ["if_role"],
        "inputs": [
            ["lan_interfaces"],
            ["backhaul_sta"],
        ],
    },
    "nm2_set_ip_assign_scheme": {
        "args_mapping": ["channel", "ht_mode", "radio_band", "ip_assign_scheme", "if_role"],
        "inputs": [
            [None, None, None, "dhcp", "lan_bridge"],
            [None, None, None, "dhcp", "primary_lan_interface"],
            [None, None, None, "dhcp", "primary_wan_interface"],
            [6, "HT40", "24g", "static", "backhaul_sta"],
            [6, "HT40", "24g", "dhcp", "backhaul_sta"],
            [44, "HT40", "5g", "static", "backhaul_sta"],
            [44, "HT40", "5g", "dhcp", "backhaul_sta"],
            [44, "HT40", "5gl", "static", "backhaul_sta"],
            [44, "HT40", "5gl", "dhcp", "backhaul_sta"],
            [157, "HT40", "5gu", "static", "backhaul_sta"],
            [157, "HT40", "5gu", "dhcp", "backhaul_sta"],
            [5, "HT40", "6g", "static", "backhaul_sta"],
            [5, "HT40", "6g", "dhcp", "backhaul_sta"],
        ],
    },
    "nm2_set_mtu": {
        "default": {
            "mtu": 1500,
        },
        "args_mapping": ["if_role"],
        "inputs": [
            ["lan_interfaces"],
            ["backhaul_sta"],
        ],
    },
    "nm2_set_nat": {
        "default": {
            "NAT": "true",
        },
        "args_mapping": ["if_role"],
        "inputs": [
            ["backhaul_sta"],
            ["primary_wan_interface"],
            ["primary_lan_interface"],
        ],
    },
    "nm2_set_netmask": {
        "default": {
            "netmask": "255.255.0.0",
        },
        "args_mapping": ["if_role"],
        "inputs": [
            ["lan_interfaces"],
            ["backhaul_sta"],
        ],
    },
    "nm2_set_upnp_mode": {
        "args_mapping": def_wifi_args,
        "inputs": def_wifi_inputs,
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
        "args_mapping": ["bridge", "interface"],
        "inputs": [
            ["br-test", "test-intf"],
        ],
    },
    "nm2_vlan_interface": {
        "default": {
            "vlan_id": 100,
        },
        "args_mapping": ["if_role"],
        "inputs": [
            ["primary_lan_interface"],
            ["primary_wan_interface"],
        ],
    },
}
