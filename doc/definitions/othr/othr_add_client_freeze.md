# Testcase othr_add_client_freeze

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify that the internet access of the connected client can be blocked, effectively
freezing the client traffic. Blocking is done by adding the rules to the `Openflow_Tag` and `Openflow_Config` tables.

## Expected outcome and pass criteria

A client is initially connected to the DUT AP, which is confirmed by inspecting the `Wifi_Associated_Clients`
table.\
The client MAC address must be present in the `Wifi_Associated_Clients` table.

Rules to freeze the client are added to the `Openflow_Tag` and `Openflow_Config` tables.\
After the rules to block the
client internet traffic are added, internet traffic for the client is blocked.

Rules to freeze a client are effectively removed by deleting the `Openflow_Tag` and `Openflow_Config` tables.\
After the
rules to block the client internet traffic are removed, internet traffic for the client is available.

Internet traffic is checked by `ping`ing the IP address `1.1.1.1`.

## Implementation status

Implemented
