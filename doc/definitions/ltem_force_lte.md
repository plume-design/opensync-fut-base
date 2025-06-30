# Testcase ltem_force_lte

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

LTE functionality must be present on the device.

## Testcase description

The goal of this testcase is to verify that the device can be forced to use the LTE backup connection by configuring the
field `force_use_lte` for the LTE interface in the OVSDB table `Lte_Config`.\
The testcase verifies that the
configuration is reflected in the `Lte_State` table.

## Expected outcome and pass criteria

Field `force_use_lte` in the `Lte_Config` table is configured and reflected in the `Lte_State` table.

## Implementation status

Implemented
