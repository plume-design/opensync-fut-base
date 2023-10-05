# Testcase nm2_set_ip_assign_scheme

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `ip_assign_scheme` field in `Wifi_Inet_Config` table is configurable and
that it can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and
verifies that the configuration is reflected in the `Wifi_Inet_State` table.\
Testcase verifies that the setting is
applied to the device - LEVEL2.

## Expected outcome and pass criteria

Field `ip_assign_scheme`, set to `dhcp` in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.\
dhcpc is alive on the device - LEVEL2.

Field `ip_assign_scheme`, set to `static` in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.\
dhcpc is dead on the device - LEVEL2.

## Implementation status

Implemented
