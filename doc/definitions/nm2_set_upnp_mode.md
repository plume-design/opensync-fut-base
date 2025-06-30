# Testcase nm2_set_upnp_mode

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

The device should be put into router mode.

A home AP should be set up and a wireless client available for testing connectivity.

The minimum required OpenSync version is 5.6.0.0.

## Testcase description

The goal of this testcase is to verify that the field `upnp_mode` in the `Wifi_Inet_Config` table is configurable and
that it can be correctly set. Testcase tests the OVSDB level by configuring the OVSDB `Wifi_Inet_Config` table and
verifies that the configuration is reflected in the `Wifi_Inet_State` table.

A wireless client is connected to the devices home AP. A UPnP client is run on the wireless client device.

The gw device checks if iptables rules contain the correct entry for port forwarding.

The testbed server device attempts to access the wireless client in the LAN network, checking if the port forwarding
works.

## Expected outcome and pass criteria

Field `upnp_mode`, set to `internal` in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.

Field `upnp_mode`, set to `external` in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.

A wireless client is able to connect to the device home AP.

The gw device contains an iptables rule for port forwarding.

The testbed server device is able to to access the wireless client in the LAN network. Port forwarding works.

Field `upnp_mode`, set to unset value in the `Wifi_Inet_Config` table, is configured and reflected in the
`Wifi_Inet_State` table.

## Implementation status

Implemented
