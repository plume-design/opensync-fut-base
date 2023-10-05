# Testcase cpm_default_listen_ip_port

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot. Ensure the OpenSync version is 5.6.0 or greater.

## Testcase description

The goal of this testcase is to verify that the IP address `127.0.0.1` and port `8888` are used as default values in
case `listenip` and `listenport` parameters are missing in the `other_config` field of the `Captive_Portal` table.

Insert an entry into the `Captive_Portal` table, where `listenip` and `listenport` parameters are missing in the
`other_config` field. The processing time for this action is approximately 2 seconds.

## Expected outcome and pass criteria

After inserting an entry into the `Captive_Portal` table, a `tinyproxy` instance is running. The `tinyproxy`
configuration file contains the text `Listen 127.0.0.1`. The `tinyproxy` configuration file contains the text
`port 8888`.

## Implementation status

Implemented
