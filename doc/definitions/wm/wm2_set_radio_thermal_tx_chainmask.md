# Testcase wm2_set_radio_thermal_tx_chainmask

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the desired thermal chainmask is applied to the DUT and is at the same time
not greater than the maximal value of the chainmask for the DUT.\
The chainmask is also applied to the system - LEVEL2.

**Important:**\
Before the actual test criteria is verified, compare `tx_chainmask` and `thermal_tx_chainmask`. Pick the
one with the lower value, which should always be `thermal_tx_chainmask` (even when they are equal). Store the value as a
value to be checked when applying `thermal_tx_chainmask`.

## Expected outcome and pass criteria

The `tx chainmask` value for the tested radio interface is applied to the `Wifi_Radio_State` table.\
Tx chainmask value
for the tested radio interface is applied to the system - LEVEL2.

After the `thermal_tx_chainmask` value for the tested radio interface is applied to the `Wifi_Radio_State`:

- `tx chainmask` value for tested radio interface is adjusted and applied to the `Wifi_Radio_State` table.
- Tx chainmask value for tested radio interface is applied to the system - LEVEL2.

## Implementation status

Implemented
