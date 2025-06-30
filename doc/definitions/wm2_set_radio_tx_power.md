# Testcase wm2_set_radio_tx_power

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the configured radio transmission power is applied on the selected radio
interface.

Set the `tx_power` field in the `Wifi_Radio_Config` table to a value supported by the device for that band. The value
must be reflected to the `Wifi_Radio_State` table.

## Expected outcome and pass criteria

The `tx_power` field in the `Wifi_Radio_Config` is reflected to the `Wifi_Radio_State` table.

## Implementation status

Implemented
