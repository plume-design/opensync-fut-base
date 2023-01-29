# Testcase fsm_configure_test_dns_parser

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

DNS category blocking aka. allowlist/denylist test.

FSM and its DNS parser should block traffic according to the policy set in the
DNS parser. FSM monitors user DNS requests, and decides if the consequent DNS
reply should be flown back to the user device, dropped or redirected to point
to a different Domain Name record (IP address).

Wireless client must be connected to the DUT and is used for triggering the DNS
traffic/requests through DUT. In this testcase, the request is supposed to be
dropped.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone
  traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.

DNS request is triggered on the client, but is blocked/dropped by tested FSM
and DNS parser according to the rules.

## Implementation status

Not Implemented
