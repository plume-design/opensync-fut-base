# Testcase fsm_gk_cache_empty_rule

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- Gatekeeper cache entries are not cleared when `FSM_Policy` entry is added
  with empty rule.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are
  configured.
- `wget` request is made on the connected client to populate entries in
  Gatekeeper cache.
- Check Gatekeeper health stats report.
- Create `FSM_Policy` table entry with empty rule.
- Check Gatekeeper health stats report again.

Gatekeeper health stats report should reflect the cached entries.\
Gatekeeper health stats report generated after `FSM_Policy` is created,
should still show the cached entries present.

## Implementation status

Not Implemented
