# Testcase fsm_verify_gk_health_stats_serviceFailures

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that in "Gatekeeper Health Stats", the
value of "serviceFailures" is incremented by 1 if FSM can reach the Gatekeeper
service, but fails to return a verdict due to some issues in the Gatekeeper
service

- This testcase starts MQTT server on RPI server and configures DUT MQTT client
to connect to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Ingress rule in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- MQTT is configured.
- Run `curl` command from the client for the same endpoint.

The "serviceFailures" value in "Gatekeeper Health Stats" is incremented by 1
each time FSM is able to reach the Gatekeeper service, but the Gatekeeper
Service fails to return a verdict due to some issues in the cloud.

## Implementation status

Not Implemented
