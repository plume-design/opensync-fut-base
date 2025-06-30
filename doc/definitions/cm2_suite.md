# Connection Manager - CM2 test suite

The `Connection Manager - CM2` is responsible for establishing connectivity to the Cloud via IPv4 or IPv6 as well as the
backhaul connection between root and leaf extender nodes.

The tests check if CM responds correctly to various connection breaks, by inspecting statuses and counters available in
the OVSDB tables `Connection_Manager_Uplink`, `Manager`, `AW_Bluetooth_Config`, `SSL`.

Cloud connectivity is realized using the following steps:

- Uplink selection.
- Get IP address based on hostname.
- Set up a connection to the `Redirector` service.
- Get an IP address for the specified Cloud deployment by the `Redirector` service.
- Connect `OpenSync` to the `Cloud`.
- Monitor link stability, repeat the process on disconnect.

The uplink selection depends on device type. If the uplink port is always cabled (ethernet, fiber, coax, etc.), no logic
is applied and the uplink port is taken at face value and only the connection to the `Cloud` is monitored. Otherwise
`CM` selects the appropriate uplink port, which is either a cabled port or a `WiFi` backhaul.
