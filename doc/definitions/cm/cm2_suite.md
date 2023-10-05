# CM2 testing

## Overview

The CM2 test suite tests Connection Manager, which is responsible for establishing the backhaul connection and keeping
connectivity to the Cloud via IPv4 or IPv6.

The tests check if CM responds correctly to various connection breaks, by inspecting statuses and counters available in
the OVSDB tables `Connection_Manager_Uplink`, `Manager`, `AW_Bluetooth_Config`, `SSL`.
