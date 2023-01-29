test_cfg = {
    "nm2_configure_nonexistent_iface": [
        {
            "if_name": "test1",
            "if_type": "eth",
            "inet_addr": "10.10.10.15",
        },
        {
            "if_name": "test2",
            "if_type": "vif",
            "inet_addr": "10.10.10.16",
        },
        {
            "if_name": "test3",
            "if_type": "bridge",
            "inet_addr": "10.10.10.17",
        },
        {
            "if_name": "test4",
            "if_type": "tap",
            "inet_addr": "10.10.10.18",
        },
    ],
    "nm2_configure_verify_native_tap_interface": [
        {
            "if_type": "tap",
            "interface": "test-intf",
        },
    ],
    "nm2_enable_disable_iface_network": [
        {
            "if_name": "eth0",
            "if_type": "eth",
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
        },
        {
            "if_name": "wifi0",
            "if_type": "vif",
        },
        {
            "if_name": "wifi1",
            "if_type": "vif",
        },
        {
            "if_name": "wifi2",
            "if_type": "vif",
        },
    ],
    "nm2_ovsdb_configure_interface_dhcpd": [
        {
            "end_pool": "10.10.10.50",
            "if_name": "eth1",
            "if_type": "eth",
            "start_pool": "10.10.10.20",
        },
        {
            "channel": 6,
            "end_pool": "10.10.10.50",
            "ht_mode": "HT40",
            "if_name": "home-ap-24",
            "if_type": "vif",
            "radio_band": "24g",
            "start_pool": "10.10.10.20",
        },
        {
            "channel": 48,
            "end_pool": "10.10.10.50",
            "ht_mode": "HT40",
            "if_name": "home-ap-l50",
            "if_type": "vif",
            "radio_band": "5gl",
            "start_pool": "10.10.10.20",
        },
        {
            "channel": 149,
            "end_pool": "10.10.10.50",
            "ht_mode": "HT40",
            "if_name": "home-ap-u50",
            "if_type": "vif",
            "radio_band": "5gu",
            "start_pool": "10.10.10.20",
        },
    ],
    "nm2_ovsdb_ip_port_forward": [
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "bhaul-sta-24",
            "src_port": "8080",
        },
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "bhaul-sta-l50",
            "src_port": "8080",
        },
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "bhaul-sta-u50",
            "src_port": "8080",
        },
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "br-home",
            "src_port": "8080",
        },
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "br-wan",
            "src_port": "8080",
        },
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "eth0",
            "src_port": "8080",
        },
        {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_ifname": "eth1",
            "src_port": "8080",
        },
    ],
    "nm2_ovsdb_remove_reinsert_iface": [
        {
            "if_name": "eth0",
            "if_type": "eth",
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
        },
        {
            "if_name": "wifi0",
            "if_type": "vif",
        },
        {
            "if_name": "wifi1",
            "if_type": "vif",
        },
        {
            "if_name": "wifi2",
            "if_type": "vif",
        },
    ],
    "nm2_set_broadcast": [
        {
            "broadcast": "10.10.10.255",
            "if_name": "eth0",
            "if_type": "eth",
        },
        {
            "broadcast": "10.10.10.255",
            "if_name": "eth1",
            "if_type": "eth",
        },
        {
            "broadcast": "10.10.10.255",
            "if_name": "wifi0",
            "if_type": "vif",
        },
        {
            "broadcast": "10.10.10.255",
            "if_name": "wifi1",
            "if_type": "vif",
        },
        {
            "broadcast": "10.10.10.255",
            "if_name": "wifi2",
            "if_type": "vif",
        },
    ],
    "nm2_set_dns": [
        {
            "if_name": "wifi0",
            "if_type": "vif",
            "primary_dns": "1.2.3.4",
            "secondary_dns": "4.5.6.7",
        },
        {
            "if_name": "wifi1",
            "if_type": "vif",
            "primary_dns": "8.9.10.11",
            "secondary_dns": "12.13.14.15",
        },
        {
            "if_name": "wifi2",
            "if_type": "vif",
            "primary_dns": "31.32.33.34",
            "secondary_dns": "34.35.36.37",
        },
        {
            "if_name": "eth0",
            "if_type": "eth",
            "primary_dns": "16.17.18.19",
            "secondary_dns": "20.21.22.23",
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
            "primary_dns": "24.25.26.27",
            "secondary_dns": "27.28.29.30",
        },
    ],
    "nm2_set_gateway": [
        {
            "gateway": "10.10.10.50",
            "if_name": "eth0",
            "if_type": "eth",
        },
        {
            "gateway": "10.10.10.50",
            "if_name": "eth1",
            "if_type": "eth",
        },
        {
            "channel": 6,
            "gateway": "10.10.10.50",
            "ht_mode": "HT40",
            "if_name": "home-ap-24",
            "if_type": "vif",
            "radio_band": "24g",
        },
        {
            "channel": 48,
            "gateway": "10.10.10.50",
            "ht_mode": "HT40",
            "if_name": "home-ap-l50",
            "if_type": "vif",
            "radio_band": "5gl",
        },
        {
            "channel": 149,
            "gateway": "10.10.10.50",
            "ht_mode": "HT40",
            "if_name": "home-ap-u50",
            "if_type": "vif",
            "radio_band": "5gu",
        },
    ],
    "nm2_set_inet_addr": [
        {
            "if_name": "wifi0",
            "if_type": "vif",
            "inet_addr": "10.10.10.30",
        },
        {
            "if_name": "wifi1",
            "if_type": "vif",
            "inet_addr": "10.10.10.30",
        },
        {
            "if_name": "wifi2",
            "if_type": "vif",
            "inet_addr": "10.10.10.30",
        },
        {
            "if_name": "eth0",
            "if_type": "eth",
            "inet_addr": "10.10.10.30",
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
            "inet_addr": "10.10.10.30",
        },
    ],
    "nm2_set_ip_assign_scheme": [
        {
            "channels": [6, 11],
            "ht_modes": ["HT40"],
            "if_name": "wifi0",
            "if_type": "vif",
            "ip_assign_scheme": "static",
            "radio_band": "24g",
        },
        {
            "channels": [36, 48],
            "ht_modes": ["HT40"],
            "if_name": "wifi1",
            "if_type": "vif",
            "ip_assign_scheme": "static",
            "radio_band": "5gl",
        },
        {
            "channels": [149, 157],
            "ht_modes": ["HT40"],
            "if_name": "wifi2",
            "if_type": "vif",
            "ip_assign_scheme": "static",
            "radio_band": "5gu",
        },
        {
            "if_name": "br-home",
            "if_type": "bridge",
            "ip_assign_scheme": "dhcp",
        },
        {
            "if_name": "eth0",
            "if_type": "eth",
            "ip_assign_scheme": "dhcp",
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
            "ip_assign_scheme": "dhcp",
        },
        {
            "channels": [6],
            "ht_modes": ["HT40"],
            "if_name": "gre-ifname-1",
            "if_type": "gre",
            "ip_assign_scheme": "dhcp",
            "radio_band": "24g",
        },
    ],
    "nm2_set_mtu": [
        {
            "if_name": "eth0",
            "if_type": "eth",
            "mtu": 2000,
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
            "mtu": 2000,
        },
        {
            "if_name": "wifi0",
            "if_type": "vif",
            "mtu": 2000,
        },
        {
            "if_name": "wifi1",
            "if_type": "vif",
            "mtu": 2000,
        },
        {
            "if_name": "wifi2",
            "if_type": "vif",
            "mtu": 2000,
        },
    ],
    "nm2_set_nat": [
        {
            "NAT": "true",
            "if_name": "eth0",
            "if_type": "eth",
        },
        {
            "NAT": "true",
            "if_name": "eth1",
            "if_type": "eth",
        },
        {
            "NAT": "true",
            "if_name": "wifi0",
            "if_type": "vif",
        },
        {
            "NAT": "true",
            "if_name": "wifi1",
            "if_type": "vif",
        },
        {
            "NAT": "true",
            "if_name": "wifi2",
            "if_type": "vif",
        },
    ],
    "nm2_set_netmask": [
        {
            "if_name": "eth0",
            "if_type": "eth",
            "netmask": "255.255.0.0",
        },
        {
            "if_name": "eth1",
            "if_type": "eth",
            "netmask": "255.255.0.0",
        },
        {
            "if_name": "wifi0",
            "if_type": "vif",
            "netmask": "255.255.0.0",
        },
        {
            "if_name": "wifi1",
            "if_type": "vif",
            "netmask": "255.255.0.0",
        },
        {
            "if_name": "wifi2",
            "if_type": "vif",
            "netmask": "255.255.0.0",
        },
    ],
    "nm2_set_upnp_mode": [
        {
            "channel": 6,
            "ht_mode": "HT40",
            "radio_band": "24g",
        },
        {
            "channel": 36,
            "ht_mode": "HT40",
            "radio_band": "5gl",
        },
        {
            "channel": 149,
            "ht_mode": "HT40",
            "radio_band": "5gu",
        },
    ],
    "nm2_verify_linux_traffic_control_rules": [
        {
            "egress_action": "action mirred egress redirect ",
            "egress_expected_str": "67",
            "egress_match": "protocol ip flower ip_proto udp src_port 67",
            "if_name": "test-intf",
            "ingress_expected_str_after_update": "8080",
            "ingress_expected_str": "80",
            "ingress_action": "action mirred egress mirror ",
            "ingress_match": "protocol ip flower ip_proto tcp src_port 80",
            "ingress_updated_match": "protocol ip flower ip_proto tcp src_port 8080",
            "priority": 11,
        },
    ],
    "nm2_verify_linux_traffic_control_template_rules": [
        {
            "egress_action": "action mirred egress redirect ",
            "egress_expected_str": "67",
            "egress_match": "protocol ip flower ip_proto udp src_port 67",
            "egress_match_with_tag": r"protocol ip flower dst_mac \${devices_tag}",
            "if_name": "test-intf",
            "ingress_action": "action mirred egress mirror ",
            "ingress_match": r"protocol ip flower dst_mac \${devices_tag}",
            "ingress_tag_name": "devices_tag",
        },
    ],
    "nm2_verify_native_bridge": [
        {
            "bridge": "br-test",
            "interface": "test-intf",
        },
    ],
    "nm2_vlan_interface": [
        {
            "parent_ifname": "eth0",
            "vlan_id": 100,
        },
        {
            "parent_ifname": "eth1",
            "vlan_id": 100,
        },
    ],
}
