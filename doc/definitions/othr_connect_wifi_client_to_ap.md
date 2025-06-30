# Testcase othr_connect_wifi_client_to_ap

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that wireless client can connect to DUT AP with a preshared key configured. Single preshared key is
configured in this testcase.

## Expected outcome and pass criteria

The client is connected to DUT AP, which is confirmed by inspecting the `Wifi_Associated_Clients` table.\
The client MAC
address must be present in the `Wifi_Associated_Clients` table.

## Implementation status

Implemented
