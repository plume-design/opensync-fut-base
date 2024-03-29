# Test case onbrd_verify_model_awlan_node

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Test case description

The goal of this test case is to verify that the field `model` in the `AWLAN_Node` table is correctly populated, and to
ensure the model string only contains allowed characters.

## Expected outcome and pass criteria

Field `model` in the `AWLAN_Node` table must be present, non-empty and equal to the `model_string` string defined in the
DUT configuration file.

Field `model` in the `AWLAN_Node` table contains only allowed characters.

## Implementation status

Implemented
