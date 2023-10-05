# Testcase fsm_test_logmacs_policy_with_gatekeeper_block

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- When Gatekeeper issues the block verdict, FSM generates the report specifying action as block.
- `logmacs` report should not be generated in this case.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- Configure DNS parser to process the DNS packets.
- Configure `logMacs` as the first policy in the `FSM_Policy` table.
- Run `wget` command from the client for the website which will be blocked by the Gatekeeper.

The Related FSM log from the connected client exists and contains the verdict received from the Gatekeeper service.\
FSM
should generate the report for for the blocked flow.

## Implementation status

Not Implemented
