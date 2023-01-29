# Testcase fcm_lan_stats_downstream_eth_behind_gw_wifi_behind_leaf

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Ethernet client must be connected to the DUT. \
WIFI client must be connected to the leaf pod. \
DUT has WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- Verify LAN Stats report is generated by the leaf pod for traffic flowing from
  ETH client connected to the gateway pod to the WiFi client connected to the
  leaf pod.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config`, `FCM_Filter` and
  `Openflow_Tag` tables are configured.
- Generate downstream traffic from the Ethernet client behind GW to the WiFi
  client behind gateway using `iperf`.

MQTT LAN stats should be generated for the downstream flow by the leaf pod.

## Implementation status

Not Implemented