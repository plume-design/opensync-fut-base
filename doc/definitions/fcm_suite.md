# Flow Collection Manager - FCM test suite

The `Flow Collection Manager - FCM` roles are:

- Collecting the network statistics at regular intervals.
- Storing the collected statistics of flows in a cache.
- Reporting the network statistics to the Cloud in a `protobuf` encoded format via `MQTT`.

The collected and reported network traffic statistics are measured between various end-clients in `LAN` and `WLAN`
networks, and also between clients in `(W)LAN` networks and devices in `WAN` networks. `FCM` provides advanced
functionalities for collecting and reporting the network statistics using filters. The `FCM` filters rules will be
applied to the network flows. The network flows are then included or excluded based on the configured filter criteria.
Filters can be applied at collection time as well as at reporting time. FCM is capable of supporting multiple plugins,
so that different types of network stats collection/reporting methods can be separately managed by the Cloud.

`FCM` currently supports these plugins:

- `Lan-to-Lan` Stats Plugin: Used to collect and report layer 2 network statistics occurring between devices within the
  `LAN` network.
- `IP Flow` Stats Plugin: Used to collect and report IP flow statistics occurring between devices in the `LAN` network
  to devices in the `WAN` network and vice-versa.
- `Per-interface Bandwidth` Stats Plugin: Tracks the total bandwidth consumed on all wired and wireless interfaces. The
  collected data:
    - Serves as an accurate count of the `WAN` data consumption.
    - Helps monitor the `WAN`-side data saturation.
    - Provides load indication for each network within the `SSID`.
