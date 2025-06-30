# Testcase wm2_wds_backhaul_topology_change

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that LEAF1 connected to the GW would
switch from being connected to the GW, to being connected to LEAF2 when
WDS is used as backhaul.\
LEAF2 has the same configuration as the GW does, with the exception of the
channel which belongs to different radio band than the one configured on the GW.\
In this testcase the LEAF1's STA would be mid-test removed and re-created, so
that would allow LEAF1 to connect to LEAF2's AP.\
After initial WDS connection is established and verified, remove LEAF1's STA
configuration, and on LEAF2 whitelist LEAF1 radio interfaces to allow LEAF1 to
connect to LEAF2.\
On LEAF1 create bhaul-sta interface with correct configuration to allow connection
to LEAF2's AP.\

## Expected outcome and pass criteria

LEAF1 is connected to LEAF2 which is verified by checking the OVSDB
`Wifi_Associated_Clients` table on LEAF2.\
Connection between nodes is WDS, which is verified by checking
`Wifi_Associated_Clients` and `Wifi_VIF_State` tables on GW.\

## Implementation status

Implemented
