# Testcase wm2_set_radio_thermal_tx_chainmask

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the desired `thermal_tx_chainmask` field in the `Wifi_Radio_Config` is
applied to the device and is at the same time not greater than the maximal value of the `tx_chainmask` field for that
interface.

**Important:**\
Before the actual test criteria is verified, compare `tx_chainmask` and `thermal_tx_chainmask`. Pick
`thermal_tx_chainmask`, which should always be lower or equal in value. Store the value as a value to be checked when
applying `thermal_tx_chainmask`.

## Expected outcome and pass criteria

The `tx chainmask` value for the tested radio interface is applied to the `Wifi_Radio_State` table.

After the `thermal_tx_chainmask` value for the tested radio interface is applied to the `Wifi_Radio_State`, the
`tx_chainmask` value for tested radio interface is adjusted to be equal to the lower of the two values and applied to
the `Wifi_Radio_State` table.

## Implementation status

Implemented
