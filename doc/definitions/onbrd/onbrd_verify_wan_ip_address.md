# Testcase onbrd_verify_wan_ip_address

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to ensure that WAN IP address is present in the
`Wifi_Inet_State` table, and is applied to the system.

**Note:**\
DHCP server on the OSRT RPI server must be running.

## Expected outcome and pass criteria

DUT WAN IP is the same as stored in the field `inet_addr` of the
`Wifi_Inet_State` table.\
DUT WAN IP is applied to the system is the same as IP of WAN interface -
LEVEL2.

## Implementation status

Implemented
