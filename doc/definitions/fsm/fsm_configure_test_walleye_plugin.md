# Testcase fsm_configure_test_walleye_plugin

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.

## Testcase description

The goal of this testcase is to verify that the FSM Walleye plugin is correctly configured.

This testcase starts MQTT server on RPI server and configures the DUT MQTT client to connect to the RPI server MQTT.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- The required tap interface is created on the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- MQTT is configured.

FSM logs indicating Walleye signature exist. Walleye signature is added to the `Object_Store_State` table.

## Implementation status

Not Implemented
