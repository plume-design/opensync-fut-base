test_inputs = {
    "nm2_configure_nonexistent_iface": {
        'args_mapping': [
            "if_name", "if_type", "inet_addr",
        ],
        'inputs': [
            ["test1", "eth", "10.10.10.15"],
            ["test2", "vif", "10.10.10.16"],
            ["test3", "bridge", "10.10.10.17"],
            ["test4", "tap", "10.10.10.18"],
        ],
    },
    "nm2_enable_disable_iface_network": {
        'inputs': [
            'FutGen|vif-phy-interfaces',
        ],
    },
    "nm2_ovsdb_configure_interface_dhcpd": {
        'default': {
            "end_pool": "10.10.10.50",
            "start_pool": "10.10.10.20",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "if_name", "if_type",
        ],
        'inputs': [
            {
                'FutGen|primary-interface-if-name-type': 'lan',
            },
            # 2.4G
            [6, "HT40", "24g", 'FutGen|vif-home-ap-by-band-and-type'],
            # 5G
            [44, "HT40", "5g", 'FutGen|vif-home-ap-by-band-and-type'],
            [157, "HT40", "5g", 'FutGen|vif-home-ap-by-band-and-type'],
            # 5GL
            [44, "HT40", "5gl", 'FutGen|vif-home-ap-by-band-and-type'],
            # 5GU
            [157, "HT40", "5gu", 'FutGen|vif-home-ap-by-band-and-type'],
            # 6G
            [5, "HT40", "6g", 'FutGen|vif-home-ap-by-band-and-type'],
            [149, "HT40", "6g", 'FutGen|vif-home-ap-by-band-and-type'],
        ],
    },
    "nm2_ovsdb_ip_port_forward": {
        'default': {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_port": "8080",
        },
        'args_mapping': [
            "src_ifname",
        ],
        'inputs': [
            {'FutGen|eth-interfaces-if-name': True},
            {'FutGen|bridge-interface-if-name': 'wan'},
            {'FutGen|vif-interfaces-if-name': "backhaul_sta"},
        ],
    },
    "nm2_ovsdb_remove_reinsert_iface": {
        'inputs': [
            "FutGen|vif-phy-interfaces",
        ],
    },
    "nm2_set_broadcast": {
        'default': {
            "broadcast": "10.10.10.255",
        },
        'inputs': [
            'FutGen|vif-phy-interfaces',
            {
                'FutGen|primary-interface-if-name-type': 'lan',
            },
        ],
    },
    "nm2_set_dns": {
        'default': {
            "primary_dns": "1.2.3.4",
            "secondary_dns": "4.5.6.7",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "if_name", "if_type", "primary_dns", "secondary_dns",
        ],
        'inputs': [
            'FutGen|eth-interfaces',
            # 2.4G
            [6, "HT40", "24g", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.1', '2.2.2.1'],
            # 5G
            [44, "HT40", "5g", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.4', '2.2.2.4'],
            [157, "HT40", "5g", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.8', '2.2.2.8'],
            # 5GL
            [44, "HT40", "5gl", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.11', '2.2.2.11'],
            # 5GU
            [157, "HT40", "5gu", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.15', '2.2.2.15'],
            # 6G
            [5, "HT40", "6g", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.18', '2.2.2.18'],
            [149, "HT40", "6g", 'FutGen|vif-home-ap-by-band-and-type', '1.1.1.22', '2.2.2.22'],
        ],
    },
    "nm2_set_gateway": {
        'default': {
            "gateway": "10.10.10.50",
        },
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "if_name", "if_type",
        ],
        'inputs': [
            'FutGen|eth-interfaces',
            # 2.4G
            [6, "HT40", "24g", 'FutGen|vif-home-ap-by-band-and-type'],
            # 5G
            [44, "HT40", "5g", 'FutGen|vif-home-ap-by-band-and-type'],
            [157, "HT40", "5g", 'FutGen|vif-home-ap-by-band-and-type'],
            # 5GL
            [44, "HT40", "5gl", 'FutGen|vif-home-ap-by-band-and-type'],
            # 5GU
            [157, "HT40", "5gu", 'FutGen|vif-home-ap-by-band-and-type'],
            # 6G
            [5, "HT40", "6g", 'FutGen|vif-home-ap-by-band-and-type'],
            [149, "HT40", "6g", 'FutGen|vif-home-ap-by-band-and-type'],
        ],
    },
    "nm2_set_inet_addr": {
        'default': {
            "inet_addr": "10.10.10.30",
        },
        'inputs': [
            'FutGen|eth-interfaces',
            'FutGen|vif-bhaul-sta-interfaces',
        ],
    },
    "nm2_set_ip_assign_scheme": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band", "ip_assign_scheme", "if_name", "if_type",
        ],
        'inputs': [
            {
                'FutGen|bridge-interface-if-name-type': 'lan',
                "ip_assign_scheme": "dhcp",
            },
            {
                'FutGen|primary-interface-if-name-type': 'lan',
                "ip_assign_scheme": "dhcp",
            },
            {
                'FutGen|primary-interface-if-name-type': 'wan',
                "ip_assign_scheme": "dhcp",
            },
            # 2.4G
            [6, "HT40", "24g", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [6, "HT40", "24g", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
            # 5G
            [44, "HT40", "5g", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [157, "HT40", "5g", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [44, "HT40", "5g", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
            [157, "HT40", "5g", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
            # 5GL
            [44, "HT40", "5gl", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [44, "HT40", "5gl", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
            # 5GU
            [157, "HT40", "5gu", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [157, "HT40", "5gu", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
            # 6G
            [5, "HT40", "6g", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [149, "HT40", "6g", 'static', 'FutGen|bhaul-sta-by-band-and-type'],
            [5, "HT40", "6g", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
            [149, "HT40", "6g", 'dhcp', 'FutGen|bhaul-sta-by-band-and-type'],
        ],
    },
    "nm2_set_mtu": {
        'default': {
            'mtu': 1500,
        },
        'inputs': [
            'FutGen|eth-interfaces',
            'FutGen|vif-bhaul-sta-interfaces',
        ],
    },
    "nm2_set_nat": {
        'default': {
            'NAT': "true",
        },
        'inputs': [
            'FutGen|vif-bhaul-sta-interfaces',
            {'FutGen|primary-interface-if-name-type': 'wan'},
        ],
    },
    "nm2_set_netmask": {
        'default': {
            "netmask": "255.255.0.0",
        },
        'inputs': [
            'FutGen|eth-interfaces',
            'FutGen|vif-bhaul-sta-interfaces',
        ],
    },
    "nm2_set_upnp_mode": {
        'args_mapping': [
            "channel", "ht_mode", "radio_band",
        ],
        'inputs': [
            [6, "HT40", "24g"],
            [44, "HT40", "5g"],
            [44, "HT40", "5gl"],
            [157, "HT40", "5g"],
            [157, "HT40", "5gu"],
            [5, "HT40", "6g"],
            [149, "HT40", "6g"],
        ],
    },
    "nm2_vlan_interface": {
        'default': {
            "vlan_id": 100,
        },
        'args_mapping': [
            "parent_ifname",
        ],
        'inputs': [
            {'FutGen|primary-interface-if-name': 'lan'},
            {'FutGen|primary-interface-if-name': 'wan'},
        ],
    },
}
