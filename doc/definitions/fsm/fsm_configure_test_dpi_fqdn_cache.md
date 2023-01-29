# Testcase fsm_configure_test_dpi_fqdn_cache

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- FSM can cache the verdict received from the Gatekeeper.
- FSM returns the verdict from the cache if present.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are
  configured.
- `dig` request is made on the connected client.

Related FSM verdict from the Gatekeeper service is cached.\
The verdict from the cache should be used for subsequent requests.

## Implementation status

Not Implemented
