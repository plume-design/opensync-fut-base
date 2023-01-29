# Testcase fcm_report_filter_pkt_lower

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.\
MQTT daemon is running on RPI Server.

## Testcase description

The goal of this testcase is to verify:

- Report should not be generated when packet count is less than the value
  configured in `pktcnt`.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config` and `FCM_Filter`
  tables are configured.
- `FCM_Filter` table is set to report when samples are greater than `pktcnt`.
- On the connected client, `iperf` or `nc` command is made to generate packets
  whose count is less then configured `pktcnt` value in the `FCM_Filter` table.

MQTT report should not be sent for flows whose count is less then configured
`pktcnt` value in the `FCM_Filter` table.

## Implementation status

Not Implemented
