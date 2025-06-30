# Testcase othr_wifi_disabled_after_removing_ap

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that Wi-Fi is disabled after AP on DUT is removed, and that a client can no
longer connect.

**Important:**\
Client is initially connected to the DUT AP. This serves as a control connection to prevent a false
positive testcase result.

## Expected outcome and pass criteria

After a client is connected to the DUT AP, AP configuration is removed. Client disconnects and cannot reconnect.

## Implementation status

Implemented
