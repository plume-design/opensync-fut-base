# Diagnostic Manager - DM test suite

The `Diagnostic Manager - DM` is spawned first during OpenSync start and is responsible for spawning other managers once
the device is ready. `DM` monitors the device, `OpenSync` processes and is also responsible for populating some OVSDB
tables like `AWLAN_Node` which is used by the cloud to identify the device and to determine how a device should be
managed.
