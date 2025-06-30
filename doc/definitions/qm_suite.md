# Queue Manager - QM test suite

The `Queue Manager - QM` is responsible for managing all `MQTT` messages from all `OpenSync` processes. It aggregates
and buffers messages in case of uplink connectivity drops, for example transient failure of backhaul connectivity, `WAN`
uplink loss, etc. The messages are encoded using `protobuf`. Multiple messages within a reporting interval are
aggregated into a single `MQTT` package. QM uses a `Unix socket` for interprocess communication.
