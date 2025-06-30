# Testcase tpsm_crash_speedtest_verify_reporting

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

The testcase configures a speed test, waits for the process instance instance and intentionally causes a crash in that
process. The correct error should be reported in the `Wifi_Speedtest_Status` table.

Ensure the `Wifi_Speedtest_Config` and `Wifi_Speedtest_Status` tables are empty.

Configure a speedtest on the device by inserting a column into the `Wifi_Speedtest_Config` table. There are several
types of speedtest available with specific configurations. The speedtest process needs to be started successfully.

The process should take some time and will not complete instantly. With a small delay (default to 1s) find the `PID` of
the process and ensure it is killed. This simulates an error in the execution of the desired type of speedtest.

Results appear in the `Wifi_Speedtest_Status` table with the same `testid` configured in `Wifi_Speedtest_Config`. Once
the `testid` column is present, the `status` should be different to `0` as we expect an error.

Any cleanup steps specific to the speedtest type should be performed after the test execution. For example the `iperf3`
type requires killing the `iperf3 server` on the testbed server.

## Expected outcome and pass criteria

The speedtest process is started. This is also logged by the `TPSM` manager in system logs.

The speedtest process is killed successfully by the test script.

The `Wifi_Speedtest_Status` table contains a column with the correct `testid`. The `status` is not `0`.

## Implementation status

Implemented
