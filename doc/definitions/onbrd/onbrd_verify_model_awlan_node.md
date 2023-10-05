# Testcase onbrd_verify_model_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the field `model` in the `AWLAN_Node` table is correctly populated.

## Expected outcome and pass criteria

Field `model` in the `AWLAN_Node` table must be present, non-empty and equal to the `model_string` string defined in the
DUT configuration file.

## Implementation status

Implemented
