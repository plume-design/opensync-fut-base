# Testcase wm2_check_wifi_credential_config

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

This testcase verifies that the OVSDB `Wifi_Credential_Config` table is not empty.\
This testcase checks if the
`Wifi_Credential_Config` table is pre-populated with Wi-Fi credential configurations.\
Credentials are populated in the
field `security` in the OVSDB table `Wifi_Credential_Config` that provides authentication details for the STA
connection.

## Expected outcome and pass criteria

The `Wifi_Credential_Config` table must exist.\
The `Wifi_Credential_Config` table is prepopulated with Wi-Fi credential
configurations.

## Implementation status

Implemented
