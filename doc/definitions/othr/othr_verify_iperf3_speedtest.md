# Testcase othr_verify_iperf3_speedtest

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

## Testcase description

Testcase verifies that Iperf3 feature works.

## Expected outcome and pass criteria

Run the `iperf3 -s -i1` on the server and run `iperf3 -c SERVER_IP` on DUT for `UP`.\
Repeat the same process
for:\
`DL`: Run `iperf3 -s -i1` on the server and run `iperf3 -c SERVER_IP -R` on DUT.\
`UDP`: Run `iperf3 -s -i1` on
the server and run `iperf3 -c SERVER_IP -u` on DUT.

The outcome of the testcase should contain a report indicating the iperf speed test was successfully executed.

## Implementation status

Implemented
