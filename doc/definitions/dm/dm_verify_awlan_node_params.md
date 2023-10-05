# Testcase dm_verify_awlan_node_params

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify the OVSDB `AWLAN_Node` table fields are being set by DM.\
Fields that are
required to be set are:

- vendor_factory
- vendor_manufacturer
- vendor_mfg_date
- vendor_name
- vendor_part_number
- sku_number
- revision
- id

## Expected outcome and pass criteria

All listed fields in the `AWLAN_Node` table must be populated and a non-empty string.

## Implementation status

Implemented
