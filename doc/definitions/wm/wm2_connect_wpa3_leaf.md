# Testcase wm2_connect_wpa3_leaf

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goals of this testcase are to verify that WPA3 AP can be created on the DUT and that leaf can connect to an AP using
the WPA3 authentication.

## Expected outcome and pass criteria

Connection is established using the WPA3 authentication:

- Leaf's `Wifi_VIF_State` table reports a connected parent in the field `parent`
- DUT's `Wifi_VIF_State` reports a connected client in the field `associated_clients`.

## Implementation status

Implemented
