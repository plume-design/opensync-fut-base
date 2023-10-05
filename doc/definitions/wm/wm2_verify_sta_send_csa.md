# Testcase wm2_verify_sta_send_csa

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that a CSA (_Channel Switch Announcement_) message is sent from the DUT and
received on REF when a channel is switched on the DUT.

## Expected outcome and pass criteria

After a channel is switched on the DUT, a log announcing that channel was switched is received on leaf, and that the
message belongs to the VIF on the DUT. The message source must be verified by checking the VIF MAC address present in
the log.

## Implementation status

Implemented
