# Testcase nm2_set_gateway

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `gateway` field in the `Wifi_Inet_Config` table is configurable and that
it can be correctly set for the eth WAN uplink interface.

The test case tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and verifies that the
configuration is reflected in the `Wifi_Inet_State` table.

The test case verifies the de-configuration of the `gateway` field in the `Wifi_Inet_Config` table.

The test case verifies that the setting is applied to the device default route.

## Expected outcome and pass criteria

The `Wifi_Inet_Config::gateway` field is configured and reflected in the `Wifi_Inet_State` table.

The gateway address is configured on the device.

The `Wifi_Inet_State::gateway` field is set to an unspecified address (`0.0.0.0` or `["set",[]]`) if the
`ip_assign_scheme` field in the `Wifi_Inet_Config` table is set to `none` and field `gateway` in the `Wifi_Inet_Config`
table is unset.

The gateway address configuration is removed from the device default route.

## Implementation status

Implemented
