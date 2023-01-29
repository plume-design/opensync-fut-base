# Testcase fsm_configure_test_http_plugin

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that the FSM HTTP plugin is correctly
configured to be able to extract the HTTP user data.\
This testcase starts MQTT Server on RPI server and configures DUT MQTT client
to connect to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Client device is successfully connected to the DUT.
- On the connected client, a curl request to the URL with a specified user agent
  is made

The related FSM log from connected client exists and contains user agent data.\
User agent is extracted from the HTTP traffic.

## Implementation status

Implemented
