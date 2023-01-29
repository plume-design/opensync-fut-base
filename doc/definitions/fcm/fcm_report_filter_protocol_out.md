# Testcase fcm_report_filter_protocol_out

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- FCM can filter the report based on the protocol number with action OUT.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter`
  tables are configured.
- `FCM_Filter` table should not report samples with configured protocol.
- On the connected client, `iperf` or `nc` command is made.

MQTT report should not be generated for the configured protocol.

## Implementation status

Not Implemented
