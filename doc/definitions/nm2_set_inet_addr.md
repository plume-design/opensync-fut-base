# Testcase nm2_set_inet_addr

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `inet_addr` in the `Wifi_Inet_Config` table is configurable and
that it can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and
verifies that the configuration is reflected in the `Wifi_Inet_State` table.\
Testcase verifies that the setting is
applied to the device - LEVEL2.

## Expected outcome and pass criteria

Field `inet_addr` in the `Wifi_Inet_Config` table is configured and reflected in the `Wifi_Inet_State` table.\
Address
is configured on the device - LEVEL2.

If field `inet_addr` in the `Wifi_Inet_Config` table is set to default, the setting is reflected in the
`Wifi_Inet_State` table.\
Address configuration is removed from the device - LEVEL2.

## Implementation status

Implemented
