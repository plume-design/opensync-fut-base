# Testcase wm2_check_radius_server_health

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The goal of this testcase is to verify if health check of RADIUS server is working properly at the DUT using FreeRADIUS
installed on RPI server.

FreeRADIUS server installed on RPI server must be configured on the DUT. Server credentials are added to the OVS table
`Radius` by populating it with the standard IP addresses, port numbers and secret passcode of both primary and secondary
FreeRadius servers. Then, update the `healthcheck_interval_seconds` field in the `RADIUS` table with non-zero value.
This will now trigger periodic health check of the configured RADIUS server every X seconds that is set in the
`healthcheck_interval_seconds` field.\\

The RADIUS server running on the RPI server is killed with `/etc/init.d/freeradius stop` to check if `healthy` field in
the `RADIUS` table gets updated with the correct status/health of the Radius server after the time set in the
`healthcheck_interval_seconds` field.

**Note:**\
Primary FreeRADIUS server can be enabled/disabled on the RPI server with: /etc/init.d/freeradius start
/etc/init.d/freeradius stop

Similarly, secondary FreeRADIUS server can be enabled/disabled on the RPI server with: /etc/init.d/freediameter start
/etc/init.d/freediameter stop

## Expected outcome and pass criteria

Testcase passes if the `healthy` field in the `RADIUS` table reports the correct health of the RADIUS server.

For instance, it can be verified as follows: Toggle `healthy` field with 'true' and 'false' values multiple times (least
3), then testcase passes if `healthy` field is reporting 'true' when FreeRADIUS server is up again.

## Implementation status

Not Implemented
