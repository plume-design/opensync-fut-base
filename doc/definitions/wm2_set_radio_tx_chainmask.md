# Testcase wm2_set_radio_tx_chainmask

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to set the `tx_chainmask` field in the `Wifi_Radio_Config` table for one interface,
effectively controlling the number of transmitting antennas, and then verify that the setting is applied to the
`Wifi_Radio_State` table.

## Expected outcome and pass criteria

The `tx_chainmask` value for the tested radio interface is applied to the `Wifi_Radio_State` table.

## Implementation status

Implemented
