# Wireless Manager - WM2 test suite

`Wireless Manager - WM2` is responsible for the setup and configuration of the `WiFi` subsystem including `VAPs`,
`SSID/Passphrase`, `Backhaul`, `Channel`, etc. `WM2` is also responsible for monitoring the `WiFi` status and client
connections and disconnections. `WM2` initially reads the current device configuration and updates the relevant
`*_Config` and `*_State` tables.

`WM2` has the following roles:

- Calls the target API implementation to configure the device upon a mismatch between these tables:
    - `Wifi_Radio_Config` vs. `Wifi_Radio_State`
    - `Wifi_VIF_Config` vs. `Wifi_VIF_State`
- Reports the connected clients and their metadata via the `Wifi_Associated_Clients` table.
- Updates the `port_active` field in the `Wifi_Master_State` table whenever an `STA VIF` link state changes in order to
    notify `CM`. This is used for onboarding and uplink connectivity of the Extenders.

## OneWifi Manager - OWM

To achieve more `unification`, `reusability` and `reliability` of the OpenSync code base, the `OneWifi Manager - OWM` is
a successor to `Wireless Manager - WM2` while also being responsible for other tasks like `steering`. The test cases
may only refer to `Wireless Manager - WM2` but are implemented agnostic to the type of wireless manager used by the
device.
