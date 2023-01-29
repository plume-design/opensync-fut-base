# Testcase fcm_lan_stats_downstream_eth_clients_behind_leaf_and_gw

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Ethernet client must be connected to the DUT. \
Ethernet clients must be connected to the leaf pod. \
DUT has WAN connectivity.\
MQTT daemon is running on RPI server.

## Testcase description

The goal of this testcase is to verify:

- LAN stats are generated for the downstream traffic generated from Ethernet
  client connected to the Gateway pod and the Ethernet client connected to the
  Ethernet client.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FCM_Collector_Config`, `AWLAN_Node`, `FCM_Report_Config`, `FCM_Filter` and
  `Openflow_Tag` tables are configured.
- Generate traffic between Ethernet clients using `iperf`.

MQTT LAN stats reports should be generated.

## Implementation status

Not Implemented
