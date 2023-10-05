# Testcase fsm_configure_test_dpi_redirect_action

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- FSM can redirect the `wget` request according to the Gatekeeper configuration and verdict.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are configured.
- `wget` request is made on the connected client.

Request is redirected to configured IP address.\
The verdict received from the Gatekeeper service is `blocked`.

## Implementation status

Implemented
