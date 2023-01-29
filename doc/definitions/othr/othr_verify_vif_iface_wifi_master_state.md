# Testcase othr_verify_vif_iface_wifi_master_state

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that the `Wifi_Master_State` table is prepopulated with
DUT STA VIF interfaces.

**Note:**\
WM must populate the `Wifi_Master_State` table. WM is the manager that uses
information from the `Wifi_Master_State` to establish upstream connection
using the preferred uplink type: wired or wireless (with STA in extender mode).

## Expected outcome and pass criteria

The `Wifi_Master_State` table exists.
The `Wifi_Master_State` table is populated with VIF interfaces.

## Implementation status

Implemented
