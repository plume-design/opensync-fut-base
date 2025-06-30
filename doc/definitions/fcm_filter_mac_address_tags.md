# Testcase fcm_filter_mac_address_tags

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- FCM can add flow samples based on the selected MAC address, specified as an `OpenFlow_Tag` value.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter` tables are configured.
- Client MAC address is configured in the `Openflow_Tag` table.
- `FCM_Filter` table is set to add samples only from the MAC address specified in the `Openflow_Tag`.
- On the connected client, `iperf` or `nc` command is made.

MQTT report should be generated for the traffic generated from the client.

## Implementation status

Not Implemented
