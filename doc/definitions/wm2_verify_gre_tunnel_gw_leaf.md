# Testcase wm2_verify_gre_tunnel_gw_leaf

## Environment setup and dependencies

Ensure GW is in OpenSync default state, as is after boot.\
GW must have WAN connectivity.\

## Testcase description

The goal of this test case is to verify that the GW is capable of establishing a GRE connection to the LEAF device.\
After establishing a GRE connection, a home AP interface is configured on the LEAF device and a wireless client is\
connected to it.\
A WAN connectivity check is then performed on the client device.

## Expected outcome and pass criteria

GW has connectivity to the LEAF device.\
LEAF has LAN connectivity via the GRE tunnel to the GW device.\
The wireless client is connected to the LEAF device.\
The wireless client has WAN connectivity via the GRE tunnel.\

## Implementation status

Implemented
