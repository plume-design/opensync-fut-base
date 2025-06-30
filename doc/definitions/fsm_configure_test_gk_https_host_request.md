# Testcase fsm_configure_test_gk_https_host_request

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
Walleye plugin is configured.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- FSM can block https flow based on request host attribute.
- Walleye DPI can retrieve host information.
- FSM sends request (of type host) to the Gatekeeper.
- FSM can process the verdict received from the Gatekeeper.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are configured.
- `wget` request is made on the connected client.

The Related FSM log from the connected client exists and contains the verdict received from the Gatekeeper
service.\
`wget` request from the client is successful when an allowed verdict is received from Gatekeeper service.

## Implementation status

Not Implemented
