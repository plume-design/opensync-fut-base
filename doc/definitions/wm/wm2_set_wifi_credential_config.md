# Testcase wm2_set_wifi_credential_config

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that the `Wifi_Credential_Config` table can be configured
with the WiFi credential configuration fields:

- ssid
- security
- onboard_type

## Expected outcome and pass criteria

The `Wifi_Credential_Config` table is correctly configured with the `ssid`,
`security` and `onboard_type` fields.

## Implementation status

Implemented
