# Testcase fcm_report_filter_dst_mac_out

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.\
MQTT daemon is running on RPI Server.

## Testcase description

The goal of this testcase is to verify:

- FCM can filter the report based on the destination MAC address with action
  OUT.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter`
  tables are configured.
- Configure `FCM_Filter` destination MAC address with action OUT.
- On the connected client, `iperf` or `nc` command is made.

MQTT report should not contain the traffic flow generated from the client since
the action is set to OUT.

## Implementation status

Not Implemented
