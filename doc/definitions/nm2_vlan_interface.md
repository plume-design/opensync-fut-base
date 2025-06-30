# Testcase nm2_vlan_interface

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

The device firmware must be compiled with the `CONFIG_OSN_LINUX_VLAN` `kconfig` option enabled.

## Testcase description

The goal of this testcase is to verify that ethernet VLAN interfaces can be configured through the `Wifi_Inet_Config`
table and the configuration is reflected in the `Wifi_Inet_State` table.

## Expected outcome and pass criteria

Fields `vlan_id` and `parent_ifname` in the `Wifi_Inet_Config` table are configured and reflected in the
`Wifi_Inet_State` table.

## Implementation status

Implemented
