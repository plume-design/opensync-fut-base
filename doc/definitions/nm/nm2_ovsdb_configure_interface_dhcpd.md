# Testcase nm2_ovsdb_configure_interface_dhcpd

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the `Wifi_Inet_Config`
dhcp server and client settings can be set correctly.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config`
table, and verifies that the configuration is reflected in the
`Wifi_Inet_State` table.\
The testcase tests if the client set interface can be disabled.\
The testcase verifies that the setting is applied to the device - LEVEL2.

## Expected outcome and pass criteria

`Wifi_Inet_Config` fields `start_pool` and `end_pool` settings are configured
and reflected in the  `Wifi_Inet_State` table.\
Settings are configured on the device - LEVEL2.

If the interface is brought down, the correct setting is configured on the
device, and if the interface is brought up again, the expected settings are
again applied to the device - LEVEL2.

## Implementation status

Implemented
