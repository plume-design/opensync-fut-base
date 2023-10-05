# Testcase nm2_vlan_interface

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the VLAN interface can be configured through the `Wifi_Inet_Config` table
and that it can be correctly set.\
Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and
verifies that the configuration is reflected in the `Wifi_Inet_State` table.\
Testcase verifies that the setting is
applied to the device - LEVEL2.

VLAN functionality must be present on the device.

## Expected outcome and pass criteria

Fields `vlan_id` and `parent_ifname` in the `Wifi_Inet_Config` table are configured and reflected in the
`Wifi_Inet_State` table.\
VLAN is configured on the device - LEVEL2.

## Implementation status

Implemented
