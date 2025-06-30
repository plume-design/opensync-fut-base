# Testcase ltem_verify_table_exists

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

LTE functionality must be present on the device.

## Testcase description

The goal of this testcase is to verify that the device supports the LTE backup functionality by verifying the existence
of the OVSDB tables `Lte_Config` and `Lte_State`.

## Expected outcome and pass criteria

`Lte_Config` and `Lte_State` tables exist.

## Implementation status

Implemented
