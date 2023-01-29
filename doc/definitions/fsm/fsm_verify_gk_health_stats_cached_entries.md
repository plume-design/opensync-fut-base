# Testcase fsm_verify_gk_health_stats_cacheEntries

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Wireless client must be connected to the DUT.\
DUT has WAN connectivity.

## Testcase description

The goal of this testcase is to verify that in "Gatekeeper Health Stats", the
value of "cachedEntries" is accurate.  The "cachedEntries" counter indicates
the number of cache entries present in the Gatekeeper cache.

- This testcase starts MQTT server on RPI server and configures the DUT MQTT
client to connect to the RPI server MQTT.

Testcase falls into category of complex "end-to-end" FSM testcases.

## Expected outcome and pass criteria

After:

- Ingress rule in the `Openflow_Config` table.
- `Flow_Service_Manager_Config` table is configured.
- MQTT is configured.
- Run `curl` command from the client for the same endpoint.

"cachedEntries" value in "Gatekeeper Health Stats" is incremented by 1 when
the entry is added to the Gatekeeper cache, and is decremented when the
entry is removed from the Gatekeeper cache.

## Implementation status

Not Implemented
