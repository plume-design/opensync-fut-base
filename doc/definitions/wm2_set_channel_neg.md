# Testcase wm2_set_channel_neg

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the mismatched channel for the selected radio interface cannot be set.

A mismatched channel is the channel from a radio band that cannot be applied to the current radio band.

The `channel` field in `Wifi_Radio_Config` is set to a valid, but unsupported channel.

## Expected outcome and pass criteria

The `channel` field in `Wifi_Radio_Config` is not reflected in the `Wifi_Radio_State` table.

## Implementation status

Implemented
