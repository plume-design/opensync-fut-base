# Testcase wm2_verify_associated_clients

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the client can associate with DUT
AP. The association is verified by inspecting the OVSDB
`Wifi_Associated_Client` table.

**Note:**\
The testcase tests wireless clients with support for WPA2 and WPA3.

## Expected outcome and pass criteria

The `Wifi_Associated_Clients` table must exist and is populated.\
Client MAC is found in the `Wifi_Associated_Clients` table.\
For a WPA2 client, field `status` must be set to `active`.\
For a WPA3 client, client must be associated to the VIF interface.

## Implementation status

Implemented
