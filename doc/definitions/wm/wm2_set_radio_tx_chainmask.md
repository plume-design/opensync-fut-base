# Testcase wm2_set_radio_tx_chainmask

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to set the Tx chainmask to the radio interface (effectively controlling the number of
transmitting antennas) and to verify that the setting is applied to the `Wifi_Radio_State` table and to the system -
LEVEL2.

## Expected outcome and pass criteria

The `tx_chainmask` value for the tested radio interface is applied to the `Wifi_Radio_State` table.\
Tx chainmask value
for the tested radio interface is applied to the system - LEVEL2.

## Implementation status

Implemented
