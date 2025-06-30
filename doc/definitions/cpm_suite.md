# Captive Portal Manager - CPM test suite

The `Captive Portal Manager - CPM` is responsible for spawning `tinyproxy` processes with the correct configurations via
entries in the `Captive_Portal` table. `Tinyproxy` forwards client `HTTPS` connections to a `captive portal` landing page
that enable authentication of third party (guest) clients in private `WiFi` networks. Guest client devices are
authenticated via external `captive portal` servers.

A `captive portal` is a splash page that automatically opens on guest user devices, prompting them to log in to access
the internet via open guest `WiFi`. Because this functionality operates at the application layer, `OpenSync` and the
`Cloud` must include the appropriate methods for establishing connections on lower layers. As soon as the node gets
user credentials, the `AAA services` can be used for client management.

`CPM` has the following roles:

- Identifying the traffic that needs to get authenticated.
- Routing the traffic to the proxy service.
- Passing the proxy service from the received HTTP port 80 traffic to the `UAM/NAS` service running in the Cloud.

`CPM` is disabled by default and is only started upon request, by updating the `Node_Services` table.
