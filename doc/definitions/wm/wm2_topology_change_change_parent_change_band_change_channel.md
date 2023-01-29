# Testcase wm2_topology_change_change_parent_change_band_change_channel

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that leaf1 connected to the gateway would
switch from being connected to the gateway to being connected to leaf2.\
Leaf2 has the same configuration as the gateway with the exception of the
channel which belongs to a different radio band than the one configured on the
gateway.\
In this testcase, the leaf1 STA would be mid-test removed and recreated, so it
becomes possible for leaf1 to connect to leaf2 AP.\
After the initial connection is established and verified, remove the leaf1 STA
configuration, and on leaf2 whitelist the leaf1 radio interfaces to allow leaf1
to connect to leaf2.\
On leaf1, create STA interface with correct configuration to allow connection
to leaf2 AP.

## Expected outcome and pass criteria

Leaf1 is connected to leaf2 which is verified by checking the OVSDB
`Wifi_Associated_Clients` table on leaf2.

## Implementation status

Implemented
