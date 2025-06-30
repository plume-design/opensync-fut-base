# Testcase fsm_gk_cache_clear_IP_entries

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- Gatekeeper IP cache entries, matching the `ipaddrs` value configured in `FSM_Policy` can be cleared.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are configured.
- `wget` request is made on the connected client to populate entries in Gatekeeper cache.
- Check the Gatekeeper health stats report.
- Create `FSM_Policy` table entry with `action` value `flush` and `ipaddrs` value set.
- Check the Gatekeeper health stats report again.

Gatekeeper health stats report should reflect the cached entries.\
The Gatekeeper health stats report generated after
`FSM_Policy` should indicate that all the cache entries matching the configured `ipaddrs` value of `FSM_Policy` are
cleared.

## Implementation status

Not Implemented
