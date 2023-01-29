# Testcase fsm_configure_test_https_sni_attributes

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- FSM DPI SNI plugin is correctly configured to be able to extract HTTP host,
  SNI and HTTP URL attributes.
- Filtering policies can be applied on these attributes.
- Gatekeeper cache functionality.

This testcase starts "dev" Gatekeeper Server on RPI server and DUT configures
Gatekeeper as the security content provider.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
-`FSM_Policy`, `Flow_Service_Manager_Config` and `Openflow_Tag` tables are
  configured.
-`curl` request to URL with specified SNI attribute is made on the connected
  client.

Related FSM log from connected client exists and contains the verdict received
from Gatekeeper service.\
`curl` request from the client is successful when an allow verdict is received
from Gatekeeper service.

## Implementation status

Not implemented
