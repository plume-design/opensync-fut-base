# Testcase onbrd_set_and_verify_bridge_mode

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the "bridge mode" settings are
correctly applied to DUT.

"Bridge mode" is a collection of settings that are pushed to DUT by the
controller, or in our case testcase script:

- NAT is disabled on WAN interface.
- IP assign scheme on WAN interface is set to `none`.
- NAT is disabled on LAN interface.
- IP assign scheme on LAN interface is set to `dhcp`.
- Configure wan-to-home bridge port.

## Expected outcome and pass criteria

The correct collection of "bridge mode" settings is applied to WAN and LAN
interfaces. This is verified by inspecting the `Wifi_Inet_State` for WAN and
LAN interfaces.

## Implementation status

Implemented
