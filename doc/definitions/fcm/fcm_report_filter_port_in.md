# Testcase fcm_report_filter_port_in

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.\
MQTT daemon is running on RPI Server.

## Testcase description

The goal of this testcase is to verify:

- FCM can filter the report based on the destination port number with action
  IN.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter`
  tables are configured.
- `FCM_Filter` table can report samples only for the configured port.
- On the connected client, `iperf` or `nc` command is made.

MQTT report should contain traffic flow destined to the configured port.

## Implementation status

Not Implemented
