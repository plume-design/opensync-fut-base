# WM2 testing

## Overview

WM2 test suite tests Wireless Manager, which is responsible for the setup and configuration of the Wi-Fi subsystem
including VAPs, SSID/Passphrase, Backhaul, Channel, etc. WM2 is also responsible for monitoring the Wi-Fi status and
client connections/disconnections.

Initially, WM2 reads the current DUT configuration and updates the relevant `Config` and `State` tables. The controller
uses a number of radios and interfaces with a model name to properly set the Adapt parameters.

WM2 has the following roles:

- Calls the target API implementation to configure the DUT upon a mismatch between these tables: `Wifi_Radio_Config` vs.
  `Wifi_Radio_State`, `Wifi_VIF_Config` vs. `Wifi_VIF_State`.
- Reports the connected clients and their metadata via the `Wifi_Associated_Clients` table.
- Updates the `Wifi_Master_State` table’s `port_active` field whenever an STA VIF link state changes in order to notify
  the CM.
