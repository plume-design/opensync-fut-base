# Testcase onbrd_verify_router_mode

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the "router mode" settings are correctly applied to the DUT.

"Router mode" is a collection of settings that are pushed to the DUT by the controller, or in our case, by the testcase
script:

- DHCP client is running on WAN interface.
- NAT is enabled on WAN interface.
- DHCP server is running on LAN interface, and has the correct settings applied.
- NAT is disabled on LAN interface.
- IP assign scheme on LAN interface is set to `static`.
- Netmask on LAN interface is set to "default".

## Expected outcome and pass criteria

The correct collection of "router mode" settings is applied to WAN and LAN interfaces. This is verified by inspecting
the `Wifi_Inet_State` fot the WAN and LAN interfaces.

## Implementation status

Implemented
