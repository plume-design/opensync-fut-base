# Testcase dm_verify_vendor_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the OVSDB `AWLAN_Node` table field
`vendor_name` holds the information about the vendor.

## Expected outcome and pass criteria

The field `vendor_name` has been correctly set by the DM. The field holds
the expected information about the vendor.

## Implementation status

Implemented
