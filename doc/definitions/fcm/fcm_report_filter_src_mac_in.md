# Testcase fcm_report_filter_src_mac_in

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- FCM can filter the report based on the source MAC address with action IN.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter` tables are configured.
- `FCM_Filter` table is set to report client stats only for the configured source MAC address.
- On the connected client, `iperf` or `nc` command is made.

MQTT report should contain traffic flow generated from the client.

## Implementation status

Not Implemented
