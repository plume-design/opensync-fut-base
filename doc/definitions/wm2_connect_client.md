# Testcase wm2_connect_client

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the client can associate with the DUT AP using the WPA3 authentication. The
association is verified by inspecting the OVSDB `Wifi_Associated_Client` table.

## Expected outcome and pass criteria

A connection between the client and the DUT is established using the WPA3 authentication.

The client MAC is found in the `Wifi_Associated_Clients` table.

## Implementation status

Implemented
