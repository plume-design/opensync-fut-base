# Testcase wm2_set_ht_mode_neg

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the mismatched HT (_High Throughput_) mode for the selected radio interface
cannot be set at the OVSDB level and to the system - LEVEL2.

## Expected outcome and pass criteria

After the HT mode is changed to the new value in the `Wifi_Radio_Config` table:

- HT mode setting is not reflected in the `Wifi_Radio_State` table.
- HT mode setting is not applied to the system - LEVEL2.

## Implementation status

Implemented
