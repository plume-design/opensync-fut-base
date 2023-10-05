# Testcase wm2_set_channel

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the channel for the selected radio interface can be set at the OVSDB level
and to the system - LEVEL2.

## Expected outcome and pass criteria

After a channel is changed to the new value in the `Wifi_Radio_Config` table:

- Channel setting is reflected in the `Wifi_Radio_State` table.
- Channel setting is applied to the system - LEVEL2.

## Implementation status

Implemented
