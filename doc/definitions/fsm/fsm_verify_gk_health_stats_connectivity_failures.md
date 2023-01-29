# Testcase fsm_verify_gk_health_stats_connectivity_failure

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that in "Gatekeeper Health Stats",
the value of "connectivityFailures" is incremented by 1 when FSM cannot
reach the Gatekeeper Service due to connection issues.

- This testcase starts MQTT Server on RPI server and configures DUT MQTT client
to connect it to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Ingress rule in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- MQTT is configured.
- Run `curl` command from the client for the same endpoint.

The "connectivityFailures" value in the "Gatekeeper Health Stats" is
incremented by 1 each time FSM fails to get the verdict from Gatekeeper service
due to connection errors.

## Implementation status

Not Implemented
