# Testcase onbrd_verify_wan_iface_mac_addr

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `hwaddr` in the OVSDB
table `Wifi_Inet_State` is equal to the DUT MAC address.

## Expected outcome and pass criteria

The field `hwaddr` in the OVSDB table `Wifi_Inet_State` is equal to DUT MAC
address.

## Implementation status

Implemented
