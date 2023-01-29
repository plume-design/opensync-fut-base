# Testcase fsm_configure_test_upnp_plugin

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that the FSM UPnP plugin is correctly
configured and the UPnP reply from client is detected.\

FUT client listens to:

- SSDP (Simple Service Discovery Protocol) message on port UDP/1900, and
  replies with a predefined response.
- HTTP GET descr.xml request, and replies with a predefined response.

Replies must be caught on the DUT by inspecting the FSM logs.

This testcase starts MQTT Server on RPI server and configures the DUT MQTT
client to connect to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Ingress rule in the `Openflow_Config` table
- `Flow_Service_Manager_Config` table is configured
- MQTT is configured
- UPnP server is started on the client device

Testcase catches the predefined log entry from FSM UPnP which includes
configured device data:

- upnp_deviceType
- upnp_friendlyName
- upnp_manufacturer
- upnp_manufacturerURL
- upnp_modelDescription
- upnp_modelName, upnp_modelNumber

## Implementation status

Implemented
