test_inputs = {
    "nm2_enable_disable_iface_network": {
        "ignore": [
            {
                "input": ["FutGen|eth-interfaces"],
            },
        ],
    },
    "nm2_ovsdb_configure_interface_dhcpd": {
        "ignore": [
            {
                "input": {"FutGen|primary-interface-if-name-type": "lan"},
            },
        ],
        "additional_inputs": [
            {"FutGen|primary-interface-if-name-type": "wan"},
        ],
    },
    "nm2_ovsdb_remove_reinsert_iface": {
        "ignore": [
            {
                "input": ["FutGen|vif-phy-interfaces"],
            },
        ],
        "additional_inputs": [
            "FutGen|vif-bhaul-sta-interfaces",
        ],
    },
}
