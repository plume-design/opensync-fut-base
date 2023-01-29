# Testcase fsm_configure_test_device_freeze

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- Device can be blocked from accessing the internet.
- FQDN request from the frozen device, should be resolved to the block page.
- Device can be unblocked by removing it from the frozen list.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone
  traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.

DNS request sent from the client is redirected when the device is in the frozen
list.

## Implementation status

Not Implemented
