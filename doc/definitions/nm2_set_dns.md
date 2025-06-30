# Testcase nm2_set_dns

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `dns` in the `Wifi_Inet_Config` table is configurable with primary
and secondary DNS, and that it is correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB
`Wifi_Inet_Config` table and verifies that the configuration is reflected in the `Wifi_Inet_State` table.\
Testcase
verifies that the setting is applied to the device - LEVEL2.

## Expected outcome and pass criteria

Field `dns` in the `Wifi_Inet_Config` table, i.e., DNS address, is configured and reflected in the `Wifi_Inet_State`
table.\
DNS primary and secondary server addresses are configured on the device - LEVEL2.

## Implementation status

Implemented
