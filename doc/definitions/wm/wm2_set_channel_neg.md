# Testcase wm2_set_channel_neg

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the mismatched channel for the
selected radio interface cannot be set at the OVSDB level and to the system -
LEVEL2.

A mismatched channel is the channel from a radio band that cannot be applied to
the current radio band.

## Expected outcome and pass criteria

After a channel is changed to the new value in the `Wifi_Radio_Config` table:

- Channel setting is not reflected in the `Wifi_Radio_State` table.
- Channel setting is not applied to the system - LEVEL2.

## Implementation status

Implemented
