# Testcase wm2_set_radio_tx_power

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that if the radio power that is in accordance with the DUT capabilities is
applied on the selected radio interface, the setting is applied to the `Wifi_Radio_Config` table, and is reflected in
the `Wifi_Radio_State` table, and is also applied to the system - LEVEL2.

## Expected outcome and pass criteria

Tx power value for the tested radio interface is reflected in the `Wifi_Radio_State` table.\
Tx power value for the
tested radio interface is applied to the system - LEVEL2.

## Implementation status

Not Implemented
