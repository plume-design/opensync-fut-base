# Testcase wm2_verify_leaf_channel_change

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the LEAF device channel switches correctly after performing a DUT channel
change. During this channel switch, the packet loss must be 0%. This is verified by constantly pinging the LEAF device
during the entire DUT channel change procedure.

## Expected outcome and pass criteria

After a channel is switched on the DUT, the LEAF device performs a channel change. The packet loss from DUT to LEAF must
be 0%.

## Implementation status

Implemented
