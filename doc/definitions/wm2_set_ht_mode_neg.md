# Testcase wm2_set_ht_mode_neg

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the mismatched `ht_mode` (channel bandwidth) for the selected radio
interface cannot be set.

A mismatched channel bandwidth is a valid channel bandwidth that cannot be applied to the current radio band.

The `ht_mode` field in `Wifi_Radio_Config` is set to a valid, but unsupported channel bandwidth.

## Expected outcome and pass criteria

The `ht_mode` field in `Wifi_Radio_Config` is not reflected to the `Wifi_Radio_State` table.

## Implementation status

Implemented
