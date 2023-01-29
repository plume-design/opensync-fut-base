# Testcase wm2_set_radio_tx_power_neg

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that if the radio power that is out of
DUT capabilities is applied to the selected radio interface, the setting is
applied to the `Wifi_Radio_Config` table, but is not reflected in the
`Wifi_Radio_State` table, and is also not applied to the system - LEVEL2.

## Expected outcome and pass criteria

Tx power value for the tested radio interface is not reflected in the
`Wifi_Radio_State` table.\
Tx power value for the tested radio interface is not applied to the system -
LEVEL2.

## Implementation status

Implemented
