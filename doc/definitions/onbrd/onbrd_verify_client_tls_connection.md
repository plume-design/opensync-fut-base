# Testcase onbrd_verify_client_tls_connection

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goals of this testcase are to confirm that DUT supports the TLS protocol and is able to connect to the "cloud
controller".

**Note:**\
FUT does not use the "cloud controller". The service is simulated by running the HAproxy service on the OSRT
RPI server.\
Both, DUT and "cloud controller" (simulation) must have correct certificates and CA files that allow
establishing a secure connection.

## Expected outcome and pass criteria

The `manager_addr` field in the `AWLAN_Node` is configured to point to the OSRT RPI server address.\
Connection status
in the `Manager` table is `ACTIVE` for at least 60 s, indicating the connection is maintained.

## Implementation status

Implemented
