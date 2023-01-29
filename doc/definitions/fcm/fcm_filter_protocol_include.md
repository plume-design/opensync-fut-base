# Testcase fcm_filter_protocol_include

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- FCM can add flow samples based on the selected protocol.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter`
  tables are configured.
- `FCM_Filter` table is set to add samples only for the UDP packets by
  specifing the protocol number.
- On the connected client, `iperf` or `nc` command is made.

CT stats should contain the traffic flow for the selected protocol (UDP).\
MQTT report should contain traffic flow from the client.

## Implementation status

Not Implemented
