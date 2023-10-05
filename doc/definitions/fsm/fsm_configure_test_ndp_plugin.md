# Testcase fsm_configure_test_ndp_plugin

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
The wireless client must be connected to the DUT.\
DUT has
WAN connectivity.

## Testcase description

The goal of this testcase is to verify that the FSM NDP (Network Discovery Protocol) plugin is correctly configured to
be able to extract the HTTP user data.

This testcase starts MQTT server on RPI server and configures the DUT MQTT client to connect to the RPI server MQTT.

Testcase falls into the category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- Required tap interfaces are created on the DUT.
- Egress and ingress rules are configured in the `Openflow_Config` table and reflected to `Openflow_State` table.
- `Flow_Service_Manager_Config` table is configured.
- MQTT is configured.

ping6 (IPv6) to a neighbor device is successful.\
Neighbor (client) is discovered and added to the `IPv6_Neighbors`
table.

## Implementation status

Not Implemented
