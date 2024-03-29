# Testcase nm2_ovsdb_ip_port_forward

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that IP port forward rule is created on the device when configured through the
OVSDB `IP_Port_Forward` or `Netfilter` tables.\
Which table is used depends on the OpenSync version the DUT is using. The used table is specified by the FUT user and
can be set in the test case input file. Examples:\

* specify the `IP_Port_Forward` table:

```python
test_inputs = {
    "nm2_ovsdb_ip_port_forward": {
        "default": {
            "dst_ipaddr": "10.10.10.123",
            "dst_port": "80",
            "protocol": "tcp",
            "src_port": "8080",
            "pf_table": "IP_Port_Forward",
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
}
```

* specify the `Netfilter` table:

```python
test_inputs = {
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
}
```

Testcase verifies that the setting is applied to the device - LEVEL2.\
Testcase verifies that the settings are deleted from the device if deleted from the `IP_Port_Forward` table.

Test is only valid if WANO (_WAN Orchestrator_) is disabled, otherwise test is not applicable for the device.

## Expected outcome and pass criteria

IP port forward is configured at the OVSDB level and on the device - LEVEL2.\
IP port forward is deleted from the OVSDB
level and from the device - LEVEL2.

## Implementation status

Implemented
