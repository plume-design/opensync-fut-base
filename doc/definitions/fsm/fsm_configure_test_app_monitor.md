# Testcase fsm_configure_test_app_monitor

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that the FSM app_dpi plugin is correctly
configured to be able to detect the application type from the flow.

This testcase starts MQTT Server on OSRT RPI server and configures DUT MQTT
client to connect it to the OSRT RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT (used to clone
  traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.
- MQTT is configured.
- On connected client `wget` command is executed.

Application type is detected and logged in the FSM logs.\
MQTT message is received with the identified application type.

## Implementation status

Not Implemented
