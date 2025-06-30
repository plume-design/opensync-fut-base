# Testcase nm2_set_nat

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `NAT` in the `Wifi_Inet_Config` table is configurable and that it
can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and verifies
that the configuration is reflected in the `Wifi_Inet_State` table.\
Testcase verifies that the setting is applied to
the device - LEVEL2.

## Expected outcome and pass criteria

Field `NAT`, set to `enabled` in the `Wifi_Inet_Config` table, is configured and reflected in the `Wifi_Inet_State`
table.\
NAT setting is applied to the device - LEVEL2. Must be ON.

Field `NAT`, set to `disabled` in the `Wifi_Inet_Config` table, is configured and reflected in the `Wifi_Inet_State`
table.\
NAT setting is applied to the device - LEVEL2. Must be OFF.

## Implementation status

Implemented
