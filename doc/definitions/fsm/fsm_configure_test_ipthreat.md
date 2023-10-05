# Testcase fsm_configure_test_ipthreat

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
Dev
Gatekeeper Docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- Inbound and Outbound IP flows can be blocked.
- FSM sends IPv4 and IPv6 request to the Gatekeeper.
- FSM can process the verdict received from the Gatekeeper.
- FSM caches the verdict received from the Gatekeeper.

This testcase starts MQTT server on RPI server and configures the DUT MQTT client to connect to the RPI server MQTT.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.

FSM logs indicating the verdict are received from the Gatekeeper. MQTT message is received when the IP flow is blocked.

## Implementation status

Not Implemented
