# Testcase wm2_topology_change_change_parent_same_band_same_channel

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that leaf1 connected the gateway would switch from being connected to the gateway
to being connected to leaf2.\
Leaf2 has the same configuration as the gateway.\
After the initial connection is
established and verified, modify value of the field `parent` in the OVSDB `Wifi_Radio_Config` table on leaf1 so that the
entry now points to leaf2 AP instead of gateway AP.

## Expected outcome and pass criteria

The connected STA on leaf1 should switch from being initially connected to gateway AP to being connected to leaf2
AP.\
Connection switch is verified by inspecting the `Wifi_Associated_Clients` table on the gateway and on leaf2.

## Implementation status

Implemented
