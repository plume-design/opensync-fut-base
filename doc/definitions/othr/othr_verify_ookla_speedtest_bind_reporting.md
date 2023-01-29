# Testcase othr_verify_ookla_speedtest_bind_reporting

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.\
Ookla speedtest binary is present on the system.

## Testcase description

Testcase verifies that *if* the speed test feature can be successfully
triggered on the DUT, then the `localIP` and `interface_name` fields in the
`Wifi_Speedtest_State` table get populated with the IP address and the
network interface that the ookla binary used during the reported speed test,
respectively.

**Note:**\
Speed test feature must be available on DUT.\
The `path` to the binary might differ from model to model.\
If the speed test fails to run, this test is passed, not failed.

## Expected outcome and pass criteria

The table `Wifi_Speedtest_Config` is initially empty. After the value is
inserted to the `test_type` field in the `Wifi_Speedtest_Config` table, the
process is started.

Wait for the results in the `Wifi_Speedtest_Status` table (**Note:** not
"State" table, but "Status").\
The wait time for speed test to finish might differ from model to model.\
The values in `localIP` and `interface_name` match the values reported
by the ookla binary, as observed in the system logs.

## Implementation status

Not implemented
