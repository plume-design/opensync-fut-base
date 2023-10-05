# Testcase fsm_verify_gk_health_stats_remotelookup

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.

## Testcase description

The goal of this testcase is to verify that in "Gatekeeper Health Stats", the value of "remoteLookups" is incremented
each time a request is sent to the Gatekeeper.

- This testcase starts MQTT server on RPI server and configures the DUT MQTT client to connect to the RPI server MQTT.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Ingress rule in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- MQTT is configured.
- Run `curl` command from the client for the same endpoint.

The "remoteLookups" value in "Gatekeeper Health Stats" is incremented by one, each time the request is sent to
Gatekeeper for receiving the verdict. The "remoteLookups" value should not be incremented if the verdict is returned
from the Gatekeeper cache.

## Implementation status

Not Implemented
