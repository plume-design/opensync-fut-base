# Testcase wpd_check_flags

## Environment setup and dependencies

Ensure DUT is in OpenSync default state, as is after boot.

To ensure that system logs capture the relevant information pertaining to the test procedure and to minimize the chance
of rotation during the test procedure, the system logs should be rotated immediately prior to starting the test
procedure.

To ensure that system logs can be captured reliably, the `log tailing command` needs to be provided, for example:

* `logread -f`
* `tail -F /var/log/messages`

## Testcase description

The testcase validates the WPD input parameters:

* wpd -d, --daemon
* wpd -a, --set-auto
* wpd -n, --set-noauto
* wpd -p, --ping
* wpd -k, --kill
* wpd -v, --verbose
* wpd -x, --proc-name proc name

Start capturing system logs into a separate file on the `tmpfs`. The goal is to filter and capture only relevant log
messages for the `WPD` process. **Note** that filtering with external tools and redirecting into a separate log file may
delay the messages as some tools have large buffers and do not flush incoming inputs immediately.

Ensure the `WPD service` on the device is stopped.

Manually start the `WPD process` with the flags `--daemon`, `--set-noauto`, `--proc-name cm`. This is the default on
most `OpenSync` systems. Allow some time for the process to start and create log messages.

Check that the exit code is `0` and a `PID` can be found, indicating the process is running in daemon mode.

Inspect the captured logs for the string `Starting WPD (Watchdog Proxy Daemon)`.

Inspect the captured logs for the string `Setting WD timeout to`. This is followed by a variable number of seconds,
depending on the precompiled value for this device.

Wait for the time period with which `wpd` pings the system watchdog.
Inspect the captured logs for the string `Got signal PING`.

To test the `--set-noauto` flag first stop `OpenSync`, so there are no pings to `WPD`. Clear the file with the captured
logs. Wait for the time period with which `wpd` pings the system watchdog. Inspect the captured logs and expect that the
string `Got signal PING` is not present.

To test the `--ping` flag, stop `OpenSync`, leave the `WPD` process in daemon mode and clear the file with the captured
logs. Provide a manual ping by executing `wpd --ping`. Inspect the captured logs for the string `Got signal PING`.

Execute `wpd --kill` and expect that the `WPD` process in daemon mode is killed.

Clear the file with the captured logs. Execute `wpd --daemon --set-auto --verbose`. `OpenSync is still stopped at this
time.

To test the `--verbose` flag, wait for the time period with which `wpd` pings the system watchdog. Inspect the captured
logs for the regex `DEBUG.*MISC: cb ping`.

To test the `--set-auto` flag, there should be pings to system watchdog without external applications. Wait for
the time period with which `wpd` pings the system watchdog. Inspect the captured logs for the string `Got signal PING`.

## Environment cleanup

Ensure that `OpenSync` is started again. Kill all system log capturing processes put in the background. Restart the
`WPD` service.

## Expected outcome and pass criteria

Manually starting the `WPD process` with the flags `--daemon`, `--set-noauto`, `--proc-name cm` exits successfully with
the `exit code 0` and a `PID` can be found, indicating the process is in daemon mode.

Captured logs contain the string `Starting WPD (Watchdog Proxy Daemon)`.

Captured logs contain the string `Setting WD timeout to`.

After the time period with which `wpd` pings the system watchdog, captured logs contain the string `Got signal PING`.

After stopping `OpenSync` the captured logs do not contain the string `Got signal PING`.

When executing `wpd --ping`, the captured logs contain the string `Got signal PING`.

When executing `wpd --kill` the `WPD` process in daemon mode is killed.

When executing `wpd --daemon --set-auto --verbose` and `OpenSync` still stopped, after the time period with which `wpd`
pings the system watchdog, captured logs contain regex `DEBUG.*MISC: cb ping`. After another time period with which
`wpd` pings the system watchdog, captured logs contain the string `Got signal PING`.

## Implementation status

Implemented
