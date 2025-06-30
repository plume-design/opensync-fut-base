# Testcase wm2_set_channel

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Set the `channel` field in `Wifi_Radio_Config` table and check if it is applied to `Wifi_Radio_State` table.

## Expected outcome and pass criteria

The `channel` field in `Wifi_Radio_Config` table is set and reflected to `Wifi_Radio_State` table.

## Implementation status

Implemented
