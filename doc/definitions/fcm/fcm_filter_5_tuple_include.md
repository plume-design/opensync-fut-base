# Testcase fcm_filter_5_tuple_include

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- FCM can add flow samples based on the configured 5-tuple.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter`
  tables are configured.
- `FCM_Filter` table is set to add samples by specifing the 5-tuple
  information.
- On the connected client, `iperf` or `nc` command is made.

CT stats should contain traffic flow for the configured 5-tuple.\
MQTT report should contain traffic flow generated for the configured 5-tuple.

## Implementation status

Not Implemented
