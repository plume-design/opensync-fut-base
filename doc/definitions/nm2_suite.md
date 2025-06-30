# Network Manager - NM2 test suite

The `Network Manager - NM2` is responsible for managing all network related configuration and network status reporting.
Its primary role is to:

- Manage the IPv4/IPv6 addresses (static, `DHCP`).
- Create and destroy network interfaces, except for Wi-Fi interfaces.
- Configure interface parameters like `MTU`, Up/Down State.
- Manage `DNS` and `DNSMASQ` services.
- Manage firewall rules like filtering and port forwarding.
- Start and stop various networking services like `UPnP`, `DHCP` server and clients.
- Manage `GRE` tunnels.
- Manage bridge interfaces.
- Reporting `DHCP` fingerprint of associated clients.
- Manage `DHCP` reserved `IP`s.

`NM` can manage `OVS bridge`, `Linux native bridge`, network interfaces and their configuration and `WiFi` interfaces
(Access Point and Station). The Cloud schema is an extension to the default OVSDB schema, which already provides all the
necessary means for configuring OVS bridges. `WiFi` interfaces cannot be fully configured without interaction with the
`WiFi` layer. For this reason, the creation semantics are more aligned with the functionality provided by the wireless
manager.
