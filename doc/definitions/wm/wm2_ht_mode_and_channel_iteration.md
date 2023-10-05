# Testcase wm2_ht_mode_and_channel_iteration

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the combination of `channel` and `ht_mode` settings is reflected from the
OVSDB `Wifi_Radio_Config` table to the `Wifi_Radio_State` table, and field `channel` to the `Wifi_VIF_State` table.

**Note:**\
The point of this testcase is not to wait for the channel to become immediately available for use. DFS
(_Dynamic Frequency Shift_) channels need to perform CAC (_Channel Availability Check_) first for the channels to become
available for use.\
The test should pass if the configuration appears in the `State` table, even if CAC is still
running.

## Expected outcome and pass criteria

`channel` and `ht_mode` settings are applied to the `Wifi_Radio_State` table.\
`channel` setting is applied to the
`Wifi_VIF_State` table.

## Implementation status

Implemented
