# Testcase wm2_wds_backhaul_line_toplogy

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this test case is to verify that a WDS backhaul can be
set up between GW and LEAF1 as well as LEAF1 and LEAF2.\
Stop DHCP server (dnsmasq) on bhaul-ap-X interface on GW and LEAF1 and stop DHCP
client on bhaul-sta interface on LEAF1 and LEAF2.\
Enable WDS on bhaul-ap-X interface on GW and LEAF1 by setting multi_ap:=backhaul_bss.\
Enable WDS on bhaul-sta-X interface on LEAF1 and LEAF2 by setting
multi_ap:=backhaul_sta.\
Configure a Line topology GW-LEAF1-LEAF2 by modifying the mac_list in Wifi_VIF_Config table.\
Monitor Wifi_VIF_Stats table to detect new WDS interfaces on GW with
mode=ap_vlan.\
Validate connected Backhaul-STA to Backhaul-BSS interface.
Based on the MAC address (ap_vlan_sta_addr) and white list, accept or decline client.\
When the client is accepted, add interface into bridge br-home.\

## Expected outcome and pass criteria

LEAF1 is connected to GW by WDS and LEAF2 is connected to LEAF1 by WDS,
which is verified by checking `Wifi_Associated_Clients` and `Wifi_VIF_State` tables on GW.

## Implementation status

Implemented
