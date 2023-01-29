# Testcase wm2_set_radio_country

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase it to verify that the `country` field in the OVSDB
table `Wifi_Radio_State` is set in accordance with the DUT regulatory domain.

**Note:**\
Radios must be configured by OpenSync prior to testcase execution. The script
will not bring up any interfaces, and will only check if the `country` field is
populated in accordance with the DUT regulatory domain for each radio.

## Expected outcome and pass criteria

The `country` field in the OVSDB table `Wifi_Radio_State` is set in accordance
with the DUT regulatory domain.

## Implementation status

Implemented
