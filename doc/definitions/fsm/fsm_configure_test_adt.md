# Testcase fsm_configure_test_adt

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
Dev Gatekeeper docker instance is running.\
Walleye plugin is configured.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that FSM can identify the device
attributes from the flow.

This testcase starts MQTT Server on RPI server and configures DUT MQTT client
to connect it to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- required tap interfaces are created on the DUT (used to clone
  traffic/requests).
- DNS egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- FSM policy is configured in the `FSM_Policy` table.
- `wget` command is run from the connected client.

MQTT message is received with the identified device attribute.

## Implementation status

Not Implemented
