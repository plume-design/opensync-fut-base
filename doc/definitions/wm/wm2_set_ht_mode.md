# Testcase wm2_set_ht_mode

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the HT (_High Throughput_) mode for
the selected radio interface can be set at the OVSDB level and to the system -
LEVEL2.

## Expected outcome and pass criteria

After the HT mode is changed to a new value in the `Wifi_Radio_Config` table:

- HT mode setting is reflected in the `Wifi_Radio_State` table.
- HT mode setting is applied to the system - LEVEL2.

## Implementation status

Implemented
