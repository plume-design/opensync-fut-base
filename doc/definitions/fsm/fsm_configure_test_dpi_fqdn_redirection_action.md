# Testcase fsm_configure_test_dpi_fqdn_redirection_action

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- FSM can redirect the `dig` request according to the Gatekeeper configuration
  and verdict.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are
  configured.
- `dig` request is made on the connected client.
- `curl` request is made on the connected client.

Request is redirected to configured IP address.\
The verdict received from the Gatekeeper service is `blocked`.

## Implementation status

Not Implemented
