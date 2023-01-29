# Testcase nm2_set_gateway

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `gateway` field in the
`Wifi_Inet_Config` table is configurable and that it can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config`
table and verifies that the configuration is reflected in the `Wifi_Inet_State`
table.\
Testcase verifies that the de-configuration of the `gateway` field in the
`Wifi_Inet_Config` table.\
Testcase verifies that the setting is applied to the device - LEVEL2.

## Expected outcome and pass criteria

Field `gateway` in the `Wifi_Inet_Config` table is configured and reflected in
the `Wifi_Inet_State` table.\
Gateway address is configured on the device - LEVEL2.

Field `gateway` in `Wifi_Inet_State` table is set to an unspecified address
(`0.0.0.0`) if `ip_assign_scheme` field in the `Wifi_Inet_Config` table is set
to `none` and field `gateway` in the `Wifi_Inet_Config` table is set to unset
value.\
Gateway address configuration is removed from the device - LEVEL2.

## Implementation status

Implemented
