# Testcase fsm_gk_cache_clear_expired_ttl

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- All the cache entries with expired Time To Live (TTL) values are removed from the Gatekeeper cache.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are configured.
- On the connected client `wget` request is made, to populate entries in Gatekeeper cache.
- Check the Gatekeeper health stats report.
- Wait until TTL expires.
- Check the Gatekeeper health stats report again.

Gatekeeper health stats report should reflect the cached entries.\
The Gatekeeper health stats report generated after
the TTL wait time, should indicate that all the cache entries with expired TTL values are cleared.

## Implementation status

Not Implemented
