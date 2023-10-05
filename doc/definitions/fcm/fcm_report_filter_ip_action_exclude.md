# Testcase fcm_report_filter_ip_action_exclude

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.\
MQTT daemon is running on RPI Server.

## Testcase description

The goal of this testcase is to verify:

- FCM report should NOT be generated for the flow if the traffic is generated from the source IP specified in src_ip
  (action set to exclude).

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter` tables are configured.
- `FCM_Filter` table is set to exclude the flows specified in the `src_ip`.
- On the connected client, `iperf` or `nc` command is made.
- MQTT report should contain traffic flow generated from the client as the action is set to exclude.

## Implementation status

Not Implemented
