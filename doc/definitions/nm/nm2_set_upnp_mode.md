# Testcase nm2_set_upnp_mode

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `upnp_mode` in the `Wifi_Inet_Config` table is configurable and
that it can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and
verifies that the configuration is reflected in the `Wifi_Inet_State` table.\
Testcase verifies that the setting is
applied to the device - LEVEL2.

## Expected outcome and pass criteria

Field `upnp_mode`, set to `internal` in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.\
Setting is applied to the device - LEVEL2.

Field `upnp_mode`, set to `external` in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.\
Setting is applied to the device - LEVEL2.

Field `upnp_mode`, set to unset value in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.\
Setting is applied to the device - LEVEL2. UPnP is removed from the device - LEVEL2.

## Implementation status

Implemented
