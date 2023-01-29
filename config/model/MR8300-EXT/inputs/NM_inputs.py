test_inputs = {
    "nm2_enable_disable_iface_network": {
        'ignore': [
            {
                'input': ['FutGen|vif-phy-interfaces'],
            },
        ],
        'additional_inputs': [
            'FutGen|vif-bhaul-sta-interfaces',
        ],
    },
    "nm2_ovsdb_remove_reinsert_iface": {
        'ignore': [
            {
                'input': ['FutGen|vif-phy-interfaces'],
            },
        ],
        'additional_inputs': [
            'FutGen|vif-bhaul-sta-interfaces',
        ],
    },
    "nm2_set_broadcast": {
        'ignore': [
            {
                'input': ['FutGen|vif-phy-interfaces'],
            },
        ],
    },
    "nm2_set_inet_addr": {
        'ignore': [
            {
                'input': ['FutGen|eth-interfaces'],
            },
        ],
    },
    "nm2_set_mtu": {
        'ignore': [
            {
                'input': ['FutGen|eth-interfaces'],
            },
        ],
    },
    "nm2_set_nat": {
        'ignore': [
            {
                'input': ['FutGen|eth-interfaces'],
            },
        ],
    },
    "nm2_set_netmask": {
        'ignore': [
            {
                'input': ['FutGen|eth-interfaces'],
            },
        ],
    },
    'nm2_vlan_interface': {
        'ignore': {
            'msg': 'NOT_APPLICABLE: VLAN not supported on device',
        },
    },
}
