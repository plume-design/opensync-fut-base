# Testcase othr_verify_gre_tunnel_dut_gw

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
DUT has a gateway role, and must have WAN connectivity.\
REF acts as a leaf.

## Testcase description

The goal of this testcase is to verify that DUT is capable of establishing a GRE
connection to the REF (leaf extender).

Steps to prepare gateway and leaf for this testcase must be done concurrently
and independently.

Gateway must be configured to have WAN connectivity.\
Gateway radios must be configured.\
Gateway backhaul AP interfaces are configured.\
Gateway bridges are configured.
Gateway GRE setup: parent GRE is created and put into the correct bridge.

Leaf GRE setup: STA interface must be configured.

## Expected outcome and pass criteria

DUT (gateway) has connectivity to REF (leaf extender).\
REF (leaf extender) has LAN connectivity via GRE tunnel to DUT (gateway).\
REF (leaf extender) has WAN connectivity via GRE tunnel to the internet.

## Implementation status

Implemented
