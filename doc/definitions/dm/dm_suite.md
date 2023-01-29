# DM Testing

## Overview

The DM suite tests the Diagnostic Manager (DM) which is the first manager to be
started. DM is responsible for spawning other managers once the device is
ready. DM overviews the device, its managers and is also responsible to
populate the OVSDB tables, e.g., `AWLAN_Node` which is used by the cloud to
identify the device and to determine how a device should be managed.
