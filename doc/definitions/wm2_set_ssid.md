# Testcase wm2_set_ssid

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the SSID for the selected VIF can be set.

## Expected outcome and pass criteria

After the SSID is changed to a new value in the `Wifi_VIF_Config` table, the SSID setting is reflected in the
`Wifi_VIF_State` table.

## Implementation status

Implemented
