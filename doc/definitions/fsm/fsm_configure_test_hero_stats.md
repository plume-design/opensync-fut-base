# Testcase fsm_configure_test_hero_stats

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify:

- HERO stats are generated periodically.
- Values reported in the HERO stats are accurate.

This testcase starts MQTT Server on RPI server and configures the DUT MQTT
client to connect to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone
  traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.

HERO metrics are reported periodically.

## Implementation status

Not Implemented
