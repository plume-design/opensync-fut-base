# Testcase wm2_set_bcn_int

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the beacon interval for the selected radio interface can be set.

## Expected outcome and pass criteria

After the beacon interval is changed to the new value in the `Wifi_Radio_Config` table, the `bcn_int` value is reflected
in the `Wifi_Radio_State` table.

## Implementation status

Implemented
