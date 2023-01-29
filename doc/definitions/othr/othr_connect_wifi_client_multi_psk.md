# Testcase othr_connect_wifi_client_multi_psk

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that a wireless client can connect to DUT AP with preshared
key configured. Multiple preshared keys are configured in this testcase.

## Expected outcome and pass criteria

The client is connected to DUT AP, with the first configured preshared key,
which is confirmed by inspecting the `Wifi_Associated_Clients` table.\
The client MAC address must be present in the `Wifi_Associated_Clients` table.

The client is connected to DUT AP, with the second configured preshared key,
which is confirmed by inspecting the `Wifi_Associated_Clients` table.\
The client MAC address must be present in the `Wifi_Associated_Clients` table.

## Implementation status

Implemented
