# Testcase dm_verify_device_mode_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the OVSDB `AWLAN_Node` table field `mode` is being correctly set by DM.

## Expected outcome and pass criteria

The field `mode` is being correctly set by DM. The field can also store an unset value.

## Implementation status

Implemented
