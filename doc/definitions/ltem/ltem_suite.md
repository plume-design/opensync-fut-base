# LTEM testing

## Overview

LTEM is responsible for switching the traffic from WAN to the LTE cellular
backup after detecting an internet outage. LTEM is working in sync with NM
and CM.

LTEM does not update the routing table when a WAN outage is detected.
After configuration of LTE via the `Lte_Config` table and the
`Wifi_Inet_Config` table, NM adds a default route for the LTE interface with a
higher route metric than that for the WAN interface.\
The lowest route metric for the default routes is the one used.\
When there is a L2 failure on the WAN interface, the default route for the WAN
interface is removed and the default route pointing at the LTE interface is the
only one remaining. CM is responsible for detecting L3 failures and triggering
a route update via the `Wifi_Route_Config` table. The only case where LTEM is
responsible for updating the routes is when the field `force_use_lte` is
configured. When that happens, LTEM updates the `Wifi_Route_Config` table to
set a higher metric for the WAN interface and this triggers NM to update the
routes.

LTEM is also responsible for adding and deleting the DNS entries for the LTE
interface during switchover.

Note: Using the LTE backup uplink requires hardware support for LTE
connectivity.
