# Testcase wm2_set_radio_vif_configs

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of the testcase is to verify the mechanism of linking radios with VIFs via the `vif_configs` field in the OVSDB
`Wifi_Radio_Config` table.\
The field points to the `uuid` of the `Wifi_VIF_Config` table for a specific interface. If
the link exists, the channel can be changed during runtime.

If the `vif_configs` field and `uuid` do not match, the radio “does not know” about the VIF, and channel change on the
radio interface should not result in the channel change of the VIF. This is the negative scenario of the testcase.

The positive testcase scenario is correct input of the `vif_configs` field, and observing the channel change on the
`VIF`.

## Expected outcome and pass criteria

The tested radio interfaces are up and have a valid configuration.

Negative scenario:

After:

- `vif_configs` field in the `Wifi_Radio_Config` table for tested radio is deleted (breaking the link).
- `channel` field in the `Wifi_Radio_Config` table with `custom_channel` is updated.

There is no channel change for the related interface in the `Wifi_VIF_State` table.

Positive scenario:

Restore the `vif_configs` field for the selected interface in the `Wifi_Radio_Config` table (establishing the link).

In the `Wifi_VIF_State` table, the `channel` field is changed.

## Implementation status

Implemented
