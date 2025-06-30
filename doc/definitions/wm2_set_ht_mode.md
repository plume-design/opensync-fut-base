# Testcase wm2_set_ht_mode

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that a `ht_mode` (channel bandwidth) for the selected radio interface can be set.

The `ht_mode` field in `Wifi_Radio_Config` is set to a valid channel bandwidth.

## Expected outcome and pass criteria

The `ht_mode` field in `Wifi_Radio_Config` is reflected to the `Wifi_Radio_State` table.

## Implementation status

Implemented
