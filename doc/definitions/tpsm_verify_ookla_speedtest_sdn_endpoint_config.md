# Testcase tpsm_verify_ookla_speedtest_sdn_endpoint_config

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Ookla speedtest binary is present on the system.

## Testcase description

Testcase verifies the configuration for the speed test feature on DUT by triggering:
`/usr/opensync/bin/ookla --upload-conn-range=16 -fjson
-c 'http://config.speedtest.net/v1/embed/x340jwcv4nz2ou3r/config' -f
human-readable`

**Note:**\
Speed test feature must be available on DUT.\\

## Expected outcome and pass criteria

The speedtest picks the most optimal server from the list. The return values are the server the speedtest connected to,
ISP, latency, download, upload and packet loss. The wait time for speed test to finish might differ from model to model.

## Implementation status

Implemented
