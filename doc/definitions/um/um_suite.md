# UM testing

## Overview

The UM suite tests the Upgrade Manager which is responsible for correct and
reliable firmware upgrades.

After receiving a trigger from the cloud, UM makes sure the device firmware
upgrade process completes. In case of FUT test suite, the cloud triggers are
simulated by controlling the fields in the OVSDB table `AWLAN_Node` which is
the table that enables communication from the cloud to the device and
vice-versa.

The cloud initiates an upgrade using:

- URL at which the firmware image is available
- Download time span during which the cloud expects the image to download
- Firmware password if the image is encrypted (optional)

Fields for communication from the cloud to the device are:

- `firmware_pass`
- `firmware_url`
- `upgrade_dl_timer`
- `upgrade_timer`

Field for communication from the device to the cloud is:

- `firmware_version`
- `upgrade_status`
