# Testcase wm2_leaf_ht_mode_change

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

This testcase verifies that the leaf changes the HT (_High Throughput_) mode when the gateway changes the HT
mode.\
Connection between DUT and REF must be established.

**Note:**\
Both the DUT and REF must be extenders for this test to be executed correctly.

## Expected outcome and pass criteria

HT mode on DUT (leaf) matches the mode set on REF (gateway).

## Implementation status

Implemented
