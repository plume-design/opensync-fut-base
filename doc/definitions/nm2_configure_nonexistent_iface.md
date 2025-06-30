# Testcase nm2_configure_nonexistent_iface

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to ensure that attempting to create a 'non-existent' interface via OpenSync with an
interface name unknown to the system does not cause OpenSync crashes or system errors.\
The interface would either be
created in the OVSDB tables or not, but must not be created on the device.\
OpenSync must not crash after this action.

"Non-existent" interface means:\
The device does not support interface of this name and will not configure it.

## Expected outcome and pass criteria

Non-existent interface is configured in the tables `Wifi_VIF_Config` or `Wifi_Inet_Config` (depending on the interface
type).\
The interface is configured in the tables `Wifi_VIF_State` or `Wifi_Inet_State` (depending on the interface
type).\
The interface is not created on the device - LEVEL2.\
OpenSync is running and has not experienced a crash.

## Implementation status

Implemented
