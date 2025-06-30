# Testcase fsm_configure_test_dpi_http_request

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
Walleye plugin is configured.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- FSM can reach a verdict based on the URL request (http).
- Walleye DPI can retrieve URL information.
- FSM sends HTTP HOST request to the Gatekeeper.
- FSM can process the verdict received from the Gatekeeper.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are configured.
- `curl` request is made on the connected client.

The Related FSM log from the connected client exists and contains the verdict received from the Gatekeeper
service.\
`curl` request from the client is successful when an allowed verdict is received from the Gatekeeper service.

## Implementation status

Implemented
