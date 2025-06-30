# Testcase wm2_topology_change_same_parent_same_band_change_channel

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that leaf1 connected to the gateway would switch from the channel that was
initially used to establish connection to the newly configured channel in the same radio band on the gateway AP.\
After
the initial connection is established and verified, modify value of the field `channel` in the OVSDB `Wifi_Radio_Config`
table to some other channel of the same radio band.

## Expected outcome and pass criteria

The connected STA on leaf1 should switch from the initial channel to a newly configured channel.\
The switch is verified
by inspecting the field `channel` in the `Wifi_Radio_State` table on leaf1.

## Implementation status

Not Implemented
