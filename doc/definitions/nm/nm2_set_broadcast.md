# Testcase nm2_set_broadcast

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `broadcast` field in the
`Wifi_Inet_Config` table is configurable and that it can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config`
table and verifies that the configuration is reflected in the `Wifi_Inet_State`
table.\
Testcase verifies that the setting is applied to the device - LEVEL2.

## Expected outcome and pass criteria

Broadcast address, i.e., `broadcast` field in the `Wifi_Inet_Config` table,
is configured and reflected in the `Wifi_Inet_State` table.\
Broadcast address is configured on the device - LEVEL2.

Field `broadcast` in the `Wifi_Inet_Config` table, set to unspecified address
(`0.0.0.0`), is reflected in the `Wifi_Inet_State` table.\
Broadcast address configuration is removed from the device - LEVEL2.

## Implementation status

Implemented
