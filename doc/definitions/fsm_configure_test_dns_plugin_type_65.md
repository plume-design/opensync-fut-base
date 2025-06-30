# Testcase fsm_configure_test_dns_plugin_type_65

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.

## Testcase description

DNS request type 65 blocking aka allowlist/denylist test.

FSM and its DNS plugin should process DNS request type 65 and block traffic according to the policy set in the DNS
plugin. FSM monitors user DNS type 65 requests, and decides if the consequent DNS reply should be flown back to the user
device, dropped or redirected to point to a different Domain Name record (IP address).

The wireless client must be connected to the DUT and is used for triggering DNS traffic/requests through DUT. In this
testcase, the request is supposed to be dropped.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.

DNS type 65 request is triggered on the client, but is blocked/dropped by the tested FSM and DNS plugin according to the
rules.

## Implementation status

Not Implemented
