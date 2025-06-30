# Testcase wm2_wds_backhaul_traffic_capture

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that 4 address frames are being
sent between nodes when WDS is used for backhaul connectivity.\
A wireless client running in monitor mode is used to capture traffic
on backhaul interfaces on the GW and LEAF nodes.\

## Expected outcome and pass criteria

Data packets captured on GW and LEAF backhaul interfaces should have
4 MAC addresses in them with their correct placement depending on
the flow of traffic.\

## Implementation status

Implemented
