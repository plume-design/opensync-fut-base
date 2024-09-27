# Testcase tpsm_verify_iperf3_speedtest

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that the Iperf3 speed test feature can be triggered on the DUT by inserting the value to the
`test_type` field in the `Wifi_Speedtest_Config` table.

Run an `iperf3 server` on the testbed server, ensuring the correct port and selecting `JSON` output.

Ensure the `Wifi_Speedtest_Config` and `Wifi_Speedtest_Status` tables are empty.
Insert the fields `test_type`, `testid`, `st_server`, `st_port`, `st_udp`, `st_dir` into  `Wifi_Speedtest_Config` table.

The `test_type` should be `IPERF3_C` which means client, if the testbed server is running a `iperf3 server`. The
`st_server` and `st_port` determine where the server is running.

The test can perform `TCP`or `UDP` traffic if the `st_udp` is set to `true`. The traffic can be limited to either upload
or download only, or both (default) with the `st_dir` field.

When the `Wifi_Speedtest_Config` table is populated, the `iperf3` process is started.

Results appear in the `Wifi_Speedtest_Status` table (**Note:** "Status", not "State" table) with the selected `testid`.
Once the `testid` column is present, the `status` should be `0` if there is no error. The `UL` and/or `DL` fields should
be populated, depending on the value of `st_dir`.

The `iperf3 server` on the testbed server should be killed after the test case is finished.

## Expected outcome and pass criteria

The `iperf3` process is started. This is also logged by the `TPSM` manager in system logs.

The `Wifi_Speedtest_Status` table contains a column with the correct `testid`, `status` should be `0`.

If `st_dir` is set to `DL_UL`, the `DL_UL` field in `Wifi_Speedtest_Status` table is populated and non-zero.
If `st_dir` is set to `DL`, the `DL` field in `Wifi_Speedtest_Status` table is populated and non-zero.
If `st_dir` is set to `UL`, the `UL` field in `Wifi_Speedtest_Status` table is populated and non-zero.

## Implementation status

Implemented
