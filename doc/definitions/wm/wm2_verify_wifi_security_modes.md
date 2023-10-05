# Testcase wm2_verify_wifi_security_modes

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the AP can be created with different Wi-Fi security modes configured:

- Open
- WPA2
- WPA3-personal
- WPA3-transition

The `Wifi_VIF_Config` table is configured with one of the available security modes.

On the client side, the same Wi-Fi security mode is configured that is used on the AP side.

**Note:**\
For simplicity reasons, the home AP and its default settings are selected to test all the above security
modes.

## Expected outcome and pass criteria

The `Wifi_VIF_State` table reports that the AP exists and is configured with the expected Wi-Fi security mode.

A client must be able to connect to the DUT AP when both are configured with the matching Wi-Fi security modes.

## Implementation status

Implemented
