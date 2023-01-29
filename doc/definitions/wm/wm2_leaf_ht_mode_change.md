# Testcase wm2_leaf_ht_mode_change

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

This testcase verifies that the leaf changes the HT (_High Throughput_) mode
when the gateway changes the HT mode.\
Connection between DUT and REF must be established.

**Note:**\
The roles of DUT and REF in OSRT are temporarily reversed. REF acts as a
gateway and DUT acts as a leaf. This is done by configuring the OSRT network
switch.

**Important:**\
After the testcase execution is finished, reverse the roles of DUT and REF to
original by reconfiguring the OSRT network switch.

## Expected outcome and pass criteria

HT mode on DUT (leaf) matches the mode set on REF (gateway).

## Implementation status

Implemented
