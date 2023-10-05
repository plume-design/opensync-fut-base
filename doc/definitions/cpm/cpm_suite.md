# CPM Testing

## Overview

The `CPM` suite tests the `Captive Portal Manager` (CPM) which is responsible for spawning `tinyproxy` processes with
the correct configurations via entries in the `Captive_Portal` table. `Tinyproxy` forwards client HTTPS connections to a
captive portal landing page.

`CPM` is disabled by default and is only started upon request, by updating the `Node_Services` table.
