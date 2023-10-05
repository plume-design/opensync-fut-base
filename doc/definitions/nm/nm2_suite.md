# NM2 testing

## Overview

NM2 test suite tests Network Manager, responsible for managing all network-related configuration and network status
reporting.\
Among others, its primary role is to:

- Manage the IPv4/IPv6 addresses (static, DHCP)
- Create and destroy network interfaces (except for Wi-Fi interfaces)
- Configure interface parameters (MTU, Up/Down State)
- Manage DNS and DNSMASQ services
- Manage firewall rules (filtering, port forwarding)
- Start/stop various networking services (UPnP, DHCP server and clients)
- Manage GRE tunnels
- Manage bridge interfaces
- Associated Client DHCP fingerprint reporting
- Manage DHCP reserved IPs
