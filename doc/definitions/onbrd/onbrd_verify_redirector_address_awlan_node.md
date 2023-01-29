# Testcase onbrd_verify_redirector_address_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `redirector_addr` is
present in the OVSDB `AWLAN_Node` table.

## Expected outcome and pass criteria

The field `redirector_addr` in the `AWLAN_Node` table is present and not empty.

## Implementation status

Implemented
