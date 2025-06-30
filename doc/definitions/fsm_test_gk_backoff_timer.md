# Testcase fsm_test_gk_backoff_timer

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- Back-off timer is triggered when FSM cannot connect to the Gatekeeper service, and sends the request to Gatekeeper
  only after the back-off timer is expired (30 seconds).

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are configured.
- Configured `gatekeeper` handler with invalid `gk_url` to simulate connection error.
- `wget` request is made multiple times on the connected client.

FSM fails to connect to the Gatekeeper service, and starts the back-off timer.\
FSM does not send the request again to
Gatekeeper until the back-off timer expires.

## Implementation status

Not Implemented
