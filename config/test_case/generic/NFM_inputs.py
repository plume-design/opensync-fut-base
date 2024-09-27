from config.defaults import def_wifi_args

test_inputs = {
    "nfm_native_ebtable_check": {
        "args_mapping": [
            "chain_name",
            "name",
            "priority",
            "rule",
            "table_name",
            "target",
            "update_target",
        ],
        "inputs": [
            ["BROUTING", "drop_dest_mac", 1, '"-d 60:b4:f7:fc:2d:44"', "broute", "DROP", "ACCEPT"],
            ["INPUT", "allow_src_mac", 10, '"-s 10:24:1d:c9:a0:27"', "filter", "DROP", "ACCEPT"],
            ["FORWARD", "multicast_drop", 10, '"-d Multicast"', "filter", "DROP", "ACCEPT"],
            ["OUTPUT", "output_arp_drop", 10, '"-p ARP"', "filter", "DROP", "ACCEPT"],
            ["PREROUTING", "prerouting_drop", 10, '"-s 11:22:33:44:55:66"', "nat", "DROP", "ACCEPT"],
            ["POSTROUTING", "postrouting_drop", 10, '"-d 66:55:44:33:22:11"', "nat", "ACCEPT", "DROP"],
            ["OUTPUT", "output_drop", 10, '""', "nat", "DROP", "CONTINUE"],
        ],
    },
    "nfm_native_ebtable_template_check": {
        "args_mapping": [
            "chain_name",
            "name",
            "priority",
            "table_name",
            "target",
            "update_target",
        ],
        "inputs": [
            ["BROUTING", "drop_dest_mac", 1, "broute", "DROP", "ACCEPT"],
            ["INPUT", "allow_src_mac", 10, "filter", "DROP", "ACCEPT"],
            ["FORWARD", "multicast_drop", 10, "filter", "DROP", "ACCEPT"],
            ["OUTPUT", "output_arp_drop", 10, "filter", "DROP", "ACCEPT"],
            ["PREROUTING", "prerouting_drop", 10, "nat", "DROP", "ACCEPT"],
            ["POSTROUTING", "postrouting_drop", 10, "nat", "ACCEPT", "DROP"],
            ["OUTPUT", "output_drop", 10, "nat", "DROP", "ACCEPT"],
        ],
    },
    "nfm_nat_loopback_check": {
        "args_mapping": def_wifi_args[:] + ["topology"],
        "inputs": [
            [44, "HT40", "5g", "line"],
            [44, "HT40", "5g", "tree"],
            [44, "HT40", "5gl", "line"],
            [44, "HT40", "5gl", "tree"],
        ],
    },
}
