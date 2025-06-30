# Testcase fcm_filter_ip_exclude

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless must be connected to the DUT.\
DUT has WAN
connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- FCM can exclude adding flow samples based on the source and destination IP addresses.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter` tables are configured.
- `FCM_Filter` table is set to exclude adding samples for the specified source and destination IP address.
- On the connected client, `iperf` or `nc` command is made.

CT stats should not contain the traffic flow for the configured source and destination IP addresses.\
MQTT report should
not contain traffic flow for the configured IP addresses.

## Implementation status

Not Implemented
