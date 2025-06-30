# Netfilter Manager - NFM test suite

The `Netfilter Manager - NFM` manages the `iptables` rules and therefore serves as the default system firewall.

`Netfilter` is a framework for controlling the data packets and data flows via the `iptables` user space utility. It
provides a wide range of packet handling capabilities such as:

- Packet filtering (Firewalling).
- Packet logging.
- Packet queueing.
- Packets mangling (i.e., for manipulating the packet headers and marking).
- Network and port address translation.
- Capturing, parsing and sending the `NFLOG` packets in `JSON` format via `MQTT`.
